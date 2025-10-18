from abc import ABC, abstractmethod
from typing import List, Optional
from services.core.domain.booking import HotelBooking
from datetime import date

class BookingRepository(ABC):
    @abstractmethod
    def save_booking(self, booking: HotelBooking) -> HotelBooking:
        raise NotImplementedError
    
    @abstractmethod
    def find_all_user_bookings(self, user_id: str) -> List[HotelBooking]:
        """Находит все броинрования конкретного пользователя"""
        raise NotImplementedError
    
    @abstractmethod
    def get_all_bookings(self) -> List[HotelBooking]:
        """Находит все бронирования в системе (только для админа)"""
        raise NotImplementedError
    
    @abstractmethod
    def get_booking_by_id(self, booking_id: str) -> Optional[HotelBooking]:
        raise NotImplementedError
    
    @abstractmethod
    def delete_booking(self, booking_id: str) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def find_overlapping_bookings(self, room_id: str, check_in: date, check_out: date) -> List[HotelBooking]:
        """Находит бронирования, которые пересекаются с заданным периодом"""
        raise NotImplementedError

    @abstractmethod
    def find_all_user_bookings(self, user_id: str) -> List[HotelBooking]:
        raise NotImplementedError