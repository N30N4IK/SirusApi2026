from abc import ABC, abstractmethod
from typing import Dict, Any

class NotificationPort(ABC):
    """Абстрактный порт для уведомлений"""

    @abstractmethod
    def send_booking_confirmation(self, recipient_email: str, booking_details: Dict[str, Any]) -> None:
        """Отправка успешного бронирования"""
        raise NotImplementedError
    
    @abstractmethod
    def send_cancellation_notification(self, recipient_email: str, booking_details: Dict[str, Any]) -> None:
        """Отправка отмены бронирования"""
        return NotImplementedError