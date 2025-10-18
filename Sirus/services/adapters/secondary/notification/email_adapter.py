from typing import Dict, Any
from services.core.ports.out.notification_port import NotificationPort

class EmailAdapter(NotificationPort):
    """Реализация порта уведомлений (временно без smpt)"""


    def send_booking_confirmation(self, recipient_email: str, booking_details: Dict[str, Any]) -> None:
        print("--- [NOTIFICATION SERVICE] ---")
        print(f"Отправка подтверждения бронирования на: {recipient_email}")
        print(f"Тема: Бронирование #{booking_details.get('booking_id')} подтверждено!")
        print(f"Детали: Отель: {booking_details.get('hotel_name', 'N/A')}, Даты: {booking_details.get('dates', 'N/A')}")
        print("------------------------------")

    def send_cancellation_notification(self, recipient_email: str, booking_details: Dict[str, Any]) -> None:
        print("--- [NOTIFICATION SERVICE] ---")
        print(f"Отправка Отмены бронирования на: {recipient_email}")
        print(f"Тема: Бронирование #{booking_details.get('booking_id')} Отмененна!")
        print(f"Детали: Отель: {booking_details.get('hotel_name', 'N/A')}, Даты: {booking_details.get('dates', 'N/A')}")
        print("------------------------------")