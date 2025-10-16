from core.ports.out.hotel_repo import HotelRepository
from core.domain.hotel import Hotel, Room, RoomType
from typing import List, Optional, Dict, Any

class HotelManagementService:
    def __init__(self, hotel_repo: HotelRepository):
        self._repo = hotel_repo

    def create_hotel(self, name: str, city: str, stars: int, description: str) -> Hotel:
        if not (1 <= stars <= 5):
            raise ValueError('Рейтинг отеля должен быть от 1 до 5 звезд')
        hotel = Hotel(name=name, city=city, stars=stars, description=description)
        return self._repo.save_hotel(hotel)
    
    def update_hotel(self, hotel_id: str, data: Dict[str, Any]) -> Hotel:
        hotel = self._repo.get_hotel_by_id(hotel_id)
        if not hotel:
            raise ValueError('Отель не найден')
        
        if 'name' in data: hotel.name = data['name']
        if 'city' in data: hotel.city = data['city']
        if 'stars' in data: 
            stars = data['stars']
            if not (1 <= stars <= 5):
                raise ValueError('Рейтинг отеля должен быть от 1 до 5 звезд')
            hotel.stars = stars

        if 'description' in data: hotel.description = data['description']

        return self._repo.save_hotel(hotel)
    
    def delete_hotel(self, hotel_id: str) -> None:
        self._repo.delete_hotel(hotel_id)



    def create_room(self, hotel_id: str, room_number: str, room_type: RoomType, capacity: int, rooms_count: int, price: float) -> Room:
        if not self._repo.get_room_by_id(hotel_id):
            raise ValueError('Номер не надйен')
        
        room = Room(
            hotel_id=hotel_id,
            room_number=room_number,
            room_type=room_type,
            capacity=capacity,
            rooms_count=rooms_count,
            price_pre_night=price
        )
        return self._repo.save_room(room)
    
    def delete_room(self, room_id: str) -> None:
        self._repo.delete_room(room_id)

    def update_room(self, room_id: str, data: Dict[str, Any]) -> Room:
        room = self._repo.get_room_by_id(room_id)
        if not room:
            raise ValueError('Номер не найден')
        
        if 'room_number' in data: room.room_number = data['room_number']
        if 'capacity' in data: room.capacity = data['capacity']
        if 'rooms_count' in data: room.rooms_count = data['rooms_count']
        if 'price_per_night' in data: room.price_per_night = data['price_per_night']

        if 'room_type' in data:
            if isinstance(data['room_type'], str):
                room.room_type = RoomType(data['room_type'])
            else:
                room.room_type = data['room_type']
        return self._repo.save_room(room)


    
    def list_hotels(self, city: Optional[str] = None, stars: Optional[int] = None, sort_by: str = 'stars') -> List[Hotel]:
        """Фильтр по городу и звездам. Упорядочивание по звездам"""
        return self._repo.find_hotels(city=city, stars=stars, sort_by=sort_by)
    
    def list_rooms(self, filters: Dict[str, Any], sort_by: str = 'price') -> List[Room]:
        """Фильтр номеров: hotel_id, capacity, rooms_count, room_type, price
        Упорядочивание по цене"""
        if 'room_type' in filters and isinstance(filters['room_type'], str):
            filters['room_type'] = RoomType(filters['room_type'])
        
        return self._repo.find_rooms(filters=filters, sort_by=sort_by)