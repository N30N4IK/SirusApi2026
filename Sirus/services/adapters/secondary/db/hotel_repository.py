from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc

from core.domain.hotel import Hotel, Room, RoomType
from core.ports.out.hotel_repo import HotelRepository
from infrastructure.database.models import HotelORM, RoomORM
from infrastructure.database.connection import SessionLocal

class SQLAlchemyHotelRepository(HotelRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_session(self) -> Session:
        return self._session_factory()
    
    def _to_domain_hotel(self, orm: HotelORM) -> Hotel:
        return Hotel(
            hotel_id=orm.hotel_id, name=orm.name, city=orm.city,
            stars=orm.stars, description=orm.description
        )
    
    def _to_domain_room(self, orm: RoomORM) -> Room:
        return Room(
            room_id=orm.room_id, hotel_id=orm.hotel_id, room_number=orm.room_number,
            room_type=orm.room_type, capacity=orm.capacity,
            rooms_count=orm.rooms_count, price_per_night=orm.price_per_night
        )
    


    def find_hotels(self, city: Optional[str] = None, stars: Optional[int] = None, sort_by: str = 'stars') -> List[Hotel]:
        with self._get_session() as session:
            query = session.query(HotelORM)


            if city:
                query = query.filter(HotelORM.city == city)
            if stars:
                query = query.filter(HotelORM.stars >= stars)
            if sort_by == 'stars':
                query = query.order_by(desc(HotelORM.stars))

            return [self._to_domain_hotel(h) for h in query.all()]
        

    def find_rooms(self, filters: Dict[str, Any], sort_by: str = 'price') -> List[Room]:
        with self._get_session() as session:
            query = session.query(RoomORM)

            if 'hotel_id' in filters:
                query = query.filter(RoomORM.hotel_id == filters["hotel_id"])
            if 'capacity' in filters:
                query = query.filter(RoomORM.capacity == filters['capacity'])
            if 'rooms_count' in filters:
                query = query.filter(RoomORM.rooms_count == filters['rooms_count'])
            if 'room_type' in filters:
                query = query.filter(RoomORM.room_type == filters['rooms_type'])
            if 'min_price' in filters:
                query = query.filter(RoomORM.price_per_night >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(RoomORM.price_per_night <= filters['max_price'])

            if sort_by == 'price_asc':
                query = query.order_by(asc(RoomORM.price_per_night))
            elif sort_by == 'price_desc':
                query = query.order_by(desc(RoomORM.price_per_night))

            return [self._to_domain_room(r) for r in query.all()]
        
    def save_hotel(self, hotel: Hotel) -> Hotel:
        """Создает или обновляет отель"""
        raise NotImplementedError
    
    def get_hotel_by_id(self, hotel_id: str) -> Optional[Hotel]:
        """Получает отель по id"""
        raise NotImplementedError
    
    def delete_hotel(self, hotel_id: str) -> None:
        """Удаляет отель"""
        raise NotImplementedError
    
    def save_room(self, room: Room) -> Room:
        """Создает или обновляет номер"""
        raise NotImplementedError
    
    def get_room_by_id(self, room_id: str) -> Optional[Room]:
        """Получает номер по id"""
        raise NotImplementedError
    
    def delete_room(self, room_id: str) -> None:
        """Удаляет номер"""
        raise NotImplementedError
        