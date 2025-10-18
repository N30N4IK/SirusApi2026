from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from services.core.domain.hotel import Hotel, Room

class HotelRepository(ABC):
    """Интерфейс для работы с хранилищем отелей и номеров"""

    @abstractmethod
    def save_hotel(self, hotel: Hotel) -> Hotel:
        """Создает или обновляет отель"""
        raise NotImplementedError
    
    @abstractmethod
    def get_hotel_by_id(self, hotel_id: str) -> Optional[Hotel]:
        """Получет отель по айди"""
        raise NotImplementedError
    
    @abstractmethod
    def delete_hotel(self, hotel_id: str) -> None:
        """Удаляет отель"""
        raise NotImplementedError


    @abstractmethod
    def find_hotels(self, city: Optional[str] = None, stars: Optional[int] = None, sort_by: str = 'stars') -> List[Hotel]:
        """Фильтрация отелей по городу и звездам, упорядочивание по звездам"""
        raise NotImplementedError

    @abstractmethod
    def save_room(self, room: Room) -> Room:
        """Создает или обновляет номер"""
        raise NotImplementedError

    @abstractmethod
    def get_room_by_id(self, room_id: str) -> Optional[Room]:
        """Получает номер по айди"""
        raise NotImplementedError
     
    @abstractmethod
    def delete_room(self, room_id: str) -> None:
        """Удаляет номер"""
        raise NotImplementedError
    
    @abstractmethod
    def find_rooms(self, filters: Dict[str, Any], sort_by: str = 'price') -> List[Room]:
        """Фильтрация номеров по отелю, параметрам, цене: Упорядочивание по цене"""
        raise NotImplementedError