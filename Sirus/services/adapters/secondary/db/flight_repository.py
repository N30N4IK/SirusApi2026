import uuid
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc

from services.core.ports.out.flight_repo import FlightRepository
from services.core.domain.flight import Flight
from services.infrastructure.database.models import FlightORM
from services.infrastructure.database.connection import SessionLocal


class SqlAlchemyFlightRepository(FlightRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_session(self) -> Session:
        return self._session_factory()
    
    def _to_domain(self, orm: FlightORM) -> Flight:
        """Преобразование ORM в доменнуб сущность"""
        return Flight(
            flight_id=orm.flight_id,
            origin_city=orm.origin_city, 
            destination_city=orm.destination_city,
            departure_time=orm.departure_time, 
            arrival_time=orm.arrival_time, 
            price=orm.price,
            total_seats=orm.total_seats, 
            booked_seats=orm.booked_seats
        )
    
    def get_all_flights(self) -> List[Flight]:
        """Возвращает список всех существующих рейсов"""
        with self._get_session() as session:
            all_flights_orm = session.query(FlightORM).all()
            return [self._to_domain(f) for f in all_flights_orm]

    def save_flight(self, flight: Flight) -> Flight:
        """Создает или обновляет рейс"""
        with self._get_session() as session:
            if flight.flight_id is None:
                flight.flight_id = str(uuid.uuid4())
                orm = FlightORM(**flight.__dict__)
                session.add(orm)
            else:
                orm = session.query(FlightORM).filter(FlightORM.flight_id == flight.flight_id).first()
                if not orm:
                    raise ValueError('Рейс для обновления не найден')

                for key, value in flight.__dict__.items():
                    if key != 'flight_id':
                         setattr(orm, key, value)

            session.commit()
            session.refresh(orm)
            return self._to_domain(orm)
        
    def delete_flight(self, flight_id: str) -> None:
        with self._get_session() as session:
            session.query(FlightORM).filter(FlightORM.flight_id == flight_id).delete()
            session.commit()

    def find_flights_by_criteria(self, origin: str, search_date: date, passengers: int) -> List[Flight]:
        """Находит все рейсы, вылетающие из указанного города, в диапозоне 48 часов от даты поиска, с достаточным кол-вом мест"""
        start_of_search_date = datetime.combine(search_date, datetime.min.time())
        start_datetime = start_of_search_date - timedelta(hours=24) # 24 часа до
        end_datetime = start_of_search_date + timedelta(hours=48)  # 48 часов после

        with self._get_session() as session:
            query = session.query(FlightORM).filter(
                FlightORM.departure_time >= start_datetime,
                FlightORM.departure_time <= end_datetime,
                # (FlightORM.total_seats - FlightORM.booked_seats) >= passengers
            )
            results = query.all()
            print(f"DEBUG REPO: Found {len(results)} raw flights in date range.") # <-- ПРИНТ 1
            
            # Теперь восстановим фильтр по местам
            final_flights = [
                self._to_domain(f) for f in results 
                if (f.total_seats - f.booked_seats) >= passengers
            ]
            print(f"DEBUG REPO: Found {len(final_flights)} flights after passenger check.") # <-- ПРИНТ 2
            return [self._to_domain(f) for f in query.all()]
        
    def update_booked_seats(self, flight_id: str, count: int) -> None:
        """Бронирует места"""
        with self._get_session() as session:
            orm = session.query(FlightORM).filter(FlightORM.flight_id == flight_id).first()
            if not orm:
                raise ValueError('Рейс не найден')
            
            if (orm.total_seats - orm.booked_seats) < count:
                raise ValueError('Недостаточно свободных мест')
            
            orm.booked_seats += count
            session.commit()