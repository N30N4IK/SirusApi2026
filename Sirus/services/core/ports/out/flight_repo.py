from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from core.domain.flight import Flight

class FlightRepository(ABC):
    """Интерфейс для работы с данными об авиарейсах"""

    @abstractmethod
    def save_flight(self, flight: Flight) -> Flight:
        """Создает или обновляет рейс"""
        raise NotImplementedError
    
    @abstractmethod
    def delete_flight(self, flight_id: str) -> None:
        """Удаляет рейс"""
        raise NotImplementedError
    
    
    @abstractmethod
    def find_flight_by_criteria(self, origin: str, date: date, passengers: int) -> List[Flight]:
        """находит все подходящие рейсы, вылетающие из указанного города в районе указанной даты, с достаточным кол-вом мест"""
        raise NotImplementedError
    
    @abstractmethod
    def update_booked_seats(self, flight_id: str, count: int) -> None:
        """Обновляет кол-во занятых мест после покупки билета"""
        raise NotImplementedError