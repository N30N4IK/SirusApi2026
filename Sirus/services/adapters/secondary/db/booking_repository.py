import uuid
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from services.core.domain.booking import HotelBooking
from services.core.ports.out.booking_repo import BookingRepository
from services.infrastructure.database.models import HotelBookingORM
from services.infrastructure.database.connection import SessionLocal

class SQLAlchemyBookingRepository(BookingRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_session(self) -> Session:
        return self._session_factory()
    
    def _to_domain(self, orm: HotelBookingORM) -> HotelBooking:
        return HotelBooking(
            booking_id=orm.booking_id,
            user_id=orm.user_id,
            room_id=orm.room_id,
            check_in_date=orm.check_in_date,
            check_out_date=orm.check_out_date,
            total_price=orm.total_price,
            is_active=orm.is_active
        )
    
    def find_all_user_bookings(self, user_id: str) -> List[HotelBooking]:
        '''Находит все бронирования конкретного пользователя'''
        with self._get_session() as session:
            query = session.query(HotelBookingORM).filter(HotelBookingORM.user_id == user_id)
            return [self._to_domain(b) for b in query.all()]
        
    def get_all_bookings(self) -> List[HotelBooking]:
        """Находит все бронирования в системе (только для админа)"""
        with self._get_session() as session:
            query = session.query(HotelBookingORM)
            return [self._to_domain(b) for b in query.all()]

    def save_booking(self, booking: HotelBooking) -> HotelBooking:
        with self._get_session() as session:
            if booking.booking_id is None:
                booking.booking_id = str(uuid.uuid4())
                orm = HotelBookingORM(**booking.__dict__)
                session.add(orm)
            else:
                orm = session.query(HotelBookingORM).filter(HotelBookingORM.booking_id == booking.booking_id).first()
                if orm is None:
                    raise ValueError(f'Бронирование с айди {booking.booking_id} не найдено')
                for key, value in booking.__dict__.items():
                    if key != 'booking_id':
                        setattr(orm, key, value)
            
            session.commit()
            session.refresh(orm)
            return self._to_domain(orm)

    def get_booking_by_id(self, booking_id: str) -> Optional[HotelBooking]:
        with self._get_session() as session:
            orm = session.query(HotelBookingORM).filter(HotelBookingORM.booking_id == booking_id).first()
            return self._to_domain(orm) if orm else None

    def delete_booking(self, booking_id: str) -> None:
        """Отмена бронирования"""
        with self._get_session() as session:
            orm = session.query(HotelBookingORM).filter(HotelBookingORM.booking_id == booking_id).first()
            if orm:
                orm.is_active = False 
                session.commit()

    def find_overlapping_bookings(self, room_id: str, check_in: date, check_out: date) -> List[HotelBooking]:
        """
        Находит все активные бронирования, которые пересекаются с заданным периодом.
        Пересечение: (start_A < end_B) AND (end_A > start_B)
        """
        with self._get_session() as session:
            query = session.query(HotelBookingORM).filter(
                HotelBookingORM.room_id == room_id,
                HotelBookingORM.is_active == True,
                and_(
                    HotelBookingORM.check_in_date < check_out,
                    HotelBookingORM.check_out_date > check_in
                )
            )
            return [self._to_domain(b) for b in query.all()]
            
    def find_all_user_bookings(self, user_id: str) -> List[HotelBooking]:
        with self._get_session() as session:
            query = session.query(HotelBookingORM).filter(HotelBookingORM.user_id == user_id)
            return [self._to_domain(b) for b in query.all()]