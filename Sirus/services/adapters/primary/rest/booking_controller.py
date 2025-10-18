from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import asdict

from services.core.usecases.room_booking import RoomBookingService
from services.core.domain.user import User
from services.infrastructure.security.auth_middleware import get_current_user, admin_required
from .booking_schemas import BookingResponse

router = APIRouter(prefix='/booking', tags=['Bookings'])

def get_room_booking_service() -> RoomBookingService:
    raise NotImplementedError

@router.get('/', response_model=List[BookingResponse], summary='Просмотр всех бронирований (Админ видит все)')
def list_all_bookings(
    user: User = Depends(get_current_user),
    service: RoomBookingService = Depends(get_room_booking_service)
):
    """Получает список всех бронирований. Если пользователь Админ, возвращает все бронирование, если просто пользователь - то только его"""
    bookings = service.list_bookings(user)
    return [BookingResponse.model_validate(asdict(b)) for b in bookings]

@router.get('/rooms/available', summary='Поиск свободных номеров по датам или длительности')
def search_available_rooms(
    check_in: date = Query(..., description='Дата заезда (YYYY-MM-DD)'),
    check_out: Optional[date] = Query(None, description='Дата выезда (YYYY-MM-DD)'),
    duration_days: Optional[int] = Query(None, ge=1, description='Кол-во дней проживания. Опционально'),
    capacity: int = Query(1, ge=1, descripption='Требуемое кол-во человек'),
    hotel_id: Optional[str] = Query(..., description='Номер отеля(Айди)'),
    service: RoomBookingService = Depends(get_room_booking_service)
):
    if check_out is None and duration_days is not None:
        check_out = check_in + timedelta(days=duration_days)
    elif check_out is None or check_out <= check_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверные даты или длительность')
    
    filters = {'hotel_id': hotel_id}

    available = service.get_available_rooms(check_in, check_out, capacity, filters)

    if not available:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Свободные места не найдено')
    
    return available

@router.post('/rooms/book', status_code=status.HTTP_201_CREATED, summary='Бронирование номера')
def book_room(
    room_id: str,
    check_in: date,
    check_out: date,
    user: User = Depends(get_current_user),
    service: RoomBookingService = Depends(get_room_booking_service)
):
    try:
        booking = service.book_room(user, room_id, check_in, check_out)
        return {'booking_id': booking.booking_id, 'status': 'Confirmed', 'total_price': booking.total_price}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.delete('/cancel/{booking_id}', summary='Отмена бронирования (Пользователю - только свою, Админу - любую)')
def cancel_booking_endpoint(
    booking_id: str,
    user: User = Depends(get_current_user),
    service: RoomBookingService = Depends(get_room_booking_service)
):
    try:
        service.cancel_booking(booking_id, user)
        return {'message': f'Бронирование {booking_id} отменено'}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        