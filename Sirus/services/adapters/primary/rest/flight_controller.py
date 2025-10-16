from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import date

from core.usecases.flight_search import FlightSearchService
from infrastructure.security.auth_middleware import admin_required
from .flight_schemas import FlightCreate, FlightUpdate, TicketRouteResponse

router = APIRouter(prefix='/flights', tags=['Flights'])

def get_flight_search_service() -> FlightSearchService:
    raise NotImplementedError

@router.get('/search', summary='Поиск авиабилетов (пряммые и с пересадкамми)')
def search_flights_endpoint(
    origin: str = Query(..., description='Город отправления'),
    destination: str = Query(..., description='Город назначения'),
    departure_date: date = Query(..., description='Дата вылета'),
    passengers: int = Query(..., description='Кол-во пассажиров'),
    service: FlightSearchService = Depends(get_flight_search_service)
):
    """Находит подходящие билеты. Если нет прямого рейса, воззвращает кратчайший путь с пересадками (макс. 24 часа пересадки)
    Помечает "Самый быстрый" и "Самый дешевый".
    """
    try:
        results = service.search_flights(origin, destination, departure_date, passengers)

        if not results:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Подходящие рейсы не найдены')
        
        return results
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f'fatal error: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error during search')
    

# --- CRUD ---

@router.post('/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)], summary='Админ: Создание нового рейса')
def create_flight(
    request: FlightCreate,
    service: FlightSearchService = Depends(get_flight_search_service)
):
    try:
        flight = service.create_flight(request.model_dump())
        return flight
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.delete('/{flight_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)], summary='Админ: Удаление рейса')
def delete_flight(
    flight_id: str,
    service: FlightSearchService = Depends(get_flight_search_service)
):
    try:
        service.delete_flight(flight_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Рейс не найден')
    return
    
