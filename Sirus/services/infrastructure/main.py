from fastapi import FastAPI
from sqlalchemy.orm import Session
from typing import Callable

from core.usecases.user_management import UserManagementService
from core.usecases.hotel_management import HotelManagementService
from core.usecases.flight_search import FlightSearchService
from core.ports.out.user_repo import UserRepository
from core.ports.out.hotel_repo import HotelRepository
from core.ports.out.notification_port import NotificationPort

from adapters.secondary.db.user_repository import SQLAlchemyUserRepository
from adapters.secondary.db.hotel_repository import SQLAlchemyHotelRepository
from adapters.secondary.db.flight_repository import SqlAlchemyFlightRepository
from adapters.secondary.notification.email_adapter import EmailAdapter

from infrastructure.database.connection import SessionLocal, create_db_and_tables
import infrastructure.security.auth_middleware 

from adapters.primary.rest import user_controller
from adapters.primary.rest import hotel_controller
from adapters.primary.rest import room_controller
from adapters.primary.rest import flight_controller

SessionLocalFactory: Callable[..., Session] = SessionLocal

user_repository_instance: UserRepository = SQLAlchemyUserRepository(
    session_factory=SessionLocalFactory
)
hotel_repository_instance: HotelRepository = SQLAlchemyHotelRepository(
    session_factory=SessionLocalFactory
)

notification_adapter_instance: NotificationPort = EmailAdapter()

user_management_service_instance: UserManagementService = UserManagementService(
    user_repo=user_repository_instance
)

hotel_management_service_instance: HotelManagementService = HotelManagementService(
    hotel_repo=hotel_repository_instance
)

flight_repository_instance = SqlAlchemyFlightRepository(session_factory=SessionLocal)

flight_search_service_instance = FlightSearchService(
    flight_repo=flight_repository_instance
)

def get_user_management_service_dependency() -> UserManagementService:
    """Провайдер для сервиса UserManagement."""
    return user_management_service_instance

def get_hotel_management_service_dependency() -> HotelManagementService:
    """Провайдер для сервиса HotelManagement."""
    return hotel_management_service_instance

def get_user_repo_dependency() -> UserRepository:
    """Провайдер для репозитория пользователей (используется в Auth Middleware)."""
    print("--- DEBUG: get_user_repo_dependency CALLED ---")
    return user_repository_instance

def get_flight_search_service_dependency() -> FlightSearchService:
    return flight_search_service_instance

app = FastAPI(
    title='Booking Aggregator API',
    description="Hexagonal architecture implementation for booking services."
)


app.dependency_overrides[
    user_controller.get_user_management_service
] = get_user_management_service_dependency

app.dependency_overrides[
    hotel_controller.get_hotel_management_service
] = get_hotel_management_service_dependency

app.dependency_overrides[
    room_controller.get_hotel_management_service
] = get_hotel_management_service_dependency

app.dependency_overrides[
    infrastructure.security.auth_middleware.get_user_repo
] = get_user_repo_dependency

app.dependency_overrides[
    flight_controller.get_flight_search_service
] = get_flight_search_service_dependency


app.include_router(user_controller.router)
app.include_router(hotel_controller.router)
app.include_router(room_controller.router)
app.include_router(flight_controller.router)

@app.on_event('startup')
def on_startup():
    """Создание таблиц при старте приложения."""
    print('Database tables check/creation...')
    create_db_and_tables()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("infrastructure.main:app", host="0.0.0.0", port=8000, reload=True)