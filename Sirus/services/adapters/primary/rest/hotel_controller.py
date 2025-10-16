from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from core.usecases.hotel_management import HotelManagementService
from core.domain.hotel import RoomType
from infrastructure.security.auth_middleware import admin_required, get_current_user
from .hotel_schemas import HotelCreateUpdate, HotelResponse

router = APIRouter(prefix='/hotels', tags=['Hotels'])


def get_hotel_management_service() -> HotelManagementService:
    raise NotImplementedError


@router.get('/', response_model=List[HotelResponse], summary='Просмотр и фильтрация отелей')
def list_hotels(
    city: Optional[str] = None,
    stars: Optional[int] = Query(None, ge=1, le=1, description='Минимальное количество звезд'),
    sort_by: str = Query('stars', pattern='^(stars|city)$'),
    service: HotelManagementService = Depends(get_hotel_management_service)
):
    """Фильтрация по городу и звездам, сортировка по звездам(по умолчанию)"""
    try:
        hotels = service.list_hotels(city=city, stars=stars, sort_by=sort_by)
        return [HotelResponse.model_validate(h) for h in hotels]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post('/', response_model=HotelResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)], summary='Админ: Создание нового отеля')
def create_hotel(
    request: HotelCreateUpdate,
    service: HotelManagementService = Depends(get_hotel_management_service)
):
    """Админ: Создание нового отеля"""
    try:
        hotel = service.create_hotel(**request.model_dump())
        return HotelResponse.model_validate(hotel)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.patch('/{hotel_id}', response_model=HotelResponse, dependencies=[Depends(admin_required)], summary='Админ: Частичное обновление отеля')
def update_hotel(
    hotel_id: str,
    request: HotelCreateUpdate,
    service: HotelManagementService = Depends(get_hotel_management_service)
):
    """Админ: Изменение отеля"""
    update_data = service.update_hotel(hotel_id, update_data)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Не переданы данные для обновления')
    
    try:
        updated_hotel = service.update_hotel(hotel_id, update_data)
        return HotelResponse.model_validate(updated_hotel)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete('/{hotel_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)], summary='Админ: Удаление отеля')
def delete_hotel(hotel_id: str, service: HotelManagementService = Depends(get_hotel_management_service)):
    """Админ: Удаление отеля"""
    service.delete_hotel(hotel_id)
    return

