from datetime import date, timedelta
from typing import List, Dict, Any

from services.core.ports.out.booking_repo import BookingRepository
from services.core.ports.out.hotel_repo import HotelRepository
from services.core.ports.out.notification_port import NotificationPort
from services.core.domain.user import User, Role
from services.core.domain.booking import HotelBooking

class RoomBookingService:
    def __init__(self, booking_repo: BookingRepository, hotel_repo: HotelRepository, notification_port: NotificationPort):
        self._booking_repo = booking_repo
        self._hotel_repo = hotel_repo
        self._notification_port = notification_port

    def list_bookings(self, requesting_user: User) -> List[HotelBooking]:
        """Возвращает все бронирования, если пользователь - админ. Или только бронирования текущего пользователя"""
        if requesting_user.role == Role.ADMIN:
            return self._booking_repo.get_all_bookings()
        else:
            return self._booking_repo.find_all_user_bookings(requesting_user.user_id)
    
    def get_available_rooms(self, check_in_date: date, check_out_date: date, required_capacity: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Находит все номера, соответствующие фильтрам, и проверяет их доступность за данный период"""
        all_candidate_rooms = self._hotel_repo.find_rooms(filters=filters, sort_by='price_asc')

        available_rooms = []
        for room in all_candidate_rooms:
            if room.capacity < required_capacity:
                continue

            overlapping = self._booking_repo.find_overlapping_bookings(
                room_id=room.room_id,
                check_in=check_in_date,
                check_out=check_out_date
            )
            if not overlapping:
                hotel = self._hotel_repo.get_hotel_by_id(room.hotel_id)
                available_rooms.append({
                    'room': room,
                    'hotel_name': hotel.name if hotel else 'N/A',
                    'total_price': room.price_per_night * (check_out_date - check_in_date).days
                })

        return available_rooms
    
    def book_room(self, user: User, room_id: str, check_in_date: date, check_out_date: date) -> HotelBooking:
        room = self._hotel_repo.get_room_by_id(room_id)
        if not room:
            raise ValueError('Номер не найден')
        
        if self._booking_repo.find_overlapping_bookings(room_id, check_in_date, check_out_date):
            raise ValueError('Номер уже занят на выбранные даты')
        
        duration = (check_out_date - check_in_date).days
        total_price = room.price_per_night * duration

        new_booking = HotelBooking(
            user_id=user.user_id,
            room_id=room.room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_price=total_price,
            booking_id=None
        )
        saved_booking = self._booking_repo.save_booking(new_booking)

        booking_details = {
            'booking_id': saved_booking.booking_id,
            'room_id':  saved_booking.room_id,
            "total_price": saved_booking.total_price
        }
        self._notification_port.send_booking_confirmation(
            recipient_email=user.email,
            booking_details=booking_details
        )
        return saved_booking
    
    def cancel_booking(self, booking_id: str, requesting_user: User):
        booking = self._booking_repo.get_booking_by_id(booking_id)

        if not booking:
            raise ValueError('Бронь не найдена')
        
        if requesting_user.role == Role.ADMIN or requesting_user.user_id == booking.user_id:
            self._booking_repo.delete_booking(booking_id)
            

            return True
        else:
            raise PermissionError('Недостаточно прав для отмены чужой брони')