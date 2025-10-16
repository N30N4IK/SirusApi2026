from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Optional, List
from core.usecases.hotel_management import HotelManagementService
from core.domain.hotel import RoomType
from infrastructure.security.auth_middleware import admin_required
from .hotel_schemas import RoomCreateUpdate, RoomResponse


router = APIRouter(prefix='/rooms', tags=['Rooms'])


def get_hotel_management_service() -> HotelManagementService:
    raise NotImplementedError

@router.get('/', response_model=List[RoomResponse], summary='Просмотр и фильтрация номеров')
def list_rooms(
    hotel_id: Optional[str] = None,
    capacity: Optional[int] = None,
    rooms_count: Optional[int] = None,
    room_type: Optional[RoomType] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = Query('price_asc', pattern='^(price_asc|price_desc)$', description="Сортировка по цене (asc/desc)"),
    service: HotelManagementService = Depends(get_hotel_management_service)
):
    """Фильтрация номеров по разл параметрам и упорядочивание по цене"""
    filters = {
        k: v for k, v in locals().items()
        if k not in ['sort_by', "service", 'self'] and v is not None
    }

    rooms = service.list_rooms(filters=filters, sort_by=sort_by)
    return [RoomResponse.model_validate(r) for r in rooms]



@router.post('/', response_model=RoomResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)], summary='Админ: Создание нового номера')
def create_room(
    request: RoomCreateUpdate,
    service: HotelManagementService = Depends(get_hotel_management_service)
):
    """Админ: Создание нового номера"""
    try:
        room = service.create_room(
            hotel_id=request.hotel_id,
            room_number=request.room_number,
            room_type=request.room_type,
            capacity=request.capacity,
            rooms_count=request.rooms_count,
            price=request.price_per_night
        )
        return RoomResponse.model_validate(room)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.patch('/{room_id}', response_model=RoomResponse, dependencies=[Depends(admin_required)], summary='Админ: Частничное обновление номера')
def updat_room_endpoint(
    room_id: str,
    request: RoomCreateUpdate,
    service: HotelManagementService = Depends(get_hotel_management_service)
):
    """Админ: Изменение параметров номера"""
    update_data = request.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Не переданны данные для обновления')
    
    try:
        updated_room = service.update_room(room_id, update_data)
        return RoomResponse.model_validate(updated_room)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete('/{room_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)], summary='Админ: Удаление номера')
def delete_room(room_id: str, service: HotelManagementService = Depends(get_hotel_management_service)):
    """Админ: Удаление номера"""
    service.delete_room(room_id)
    return

