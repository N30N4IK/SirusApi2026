from fastapi import FastAPI
from sqlalchemy.orm import Session
from typing import Callable
# Коры
from services.core.usecases.user_management import UserManagementService
from services.core.usecases.hotel_management import HotelManagementService
from services.core.usecases.flight_search import FlightSearchService
from services.core.usecases.room_booking import RoomBookingService
from services.core.ports.out.user_repo import UserRepository
from services.core.ports.out.hotel_repo import HotelRepository
from services.core.ports.out.notification_port import NotificationPort
from services.core.ports.out.booking_repo import BookingRepository
# Адаптеры
from services.adapters.secondary.db.user_repository import SQLAlchemyUserRepository
from services.adapters.secondary.db.hotel_repository import SQLAlchemyHotelRepository
from services.adapters.secondary.db.flight_repository import SqlAlchemyFlightRepository
from services.adapters.secondary.db.booking_repository import SQLAlchemyBookingRepository
from services.adapters.secondary.notification.email_adapter import EmailAdapter
# Инфраструктура
from services.infrastructure.database.connection import SessionLocal, create_db_and_tables
import services.infrastructure.security.auth_middleware as auth_middleware_module
# Еще адаптеры
from services.adapters.primary.rest import user_controller
from services.adapters.primary.rest import hotel_controller
from services.adapters.primary.rest import room_controller
from services.adapters.primary.rest import flight_controller
from services.adapters.primary.rest import booking_controller

SessionLocalFactory: Callable[..., Session] = SessionLocal

user_repository_instance: UserRepository = SQLAlchemyUserRepository(
    session_factory=SessionLocalFactory)
hotel_repository_instance: HotelRepository = SQLAlchemyHotelRepository(
    session_factory=SessionLocalFactory)
booking_repository_instance: BookingRepository = SQLAlchemyBookingRepository(
    session_factory=SessionLocalFactory)
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

room_booking_service_instance: RoomBookingService = RoomBookingService(
    booking_repo=booking_repository_instance,
    hotel_repo=hotel_repository_instance,
    notification_port=notification_adapter_instance
)

def get_user_management_service_dependency() -> UserManagementService:
    """Провайдер для сервиса UserManagement."""
    return user_management_service_instance

def get_hotel_management_service_dependency() -> HotelManagementService:
    """Провайдер для сервиса HotelManagement."""
    return hotel_management_service_instance

def get_user_repo_dependency() -> UserRepository:
    """Провайдер для репозитория пользователей (используется в Auth Middleware)."""
    return user_repository_instance

def get_flight_search_service_dependency() -> FlightSearchService:
    return flight_search_service_instance

def get_room_booking_service_dependency() -> RoomBookingService:
    return room_booking_service_instance


app = FastAPI(
    title='Sirus Hexagonal API',
    description="Hexagonal architecture"
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
    flight_controller.get_flight_search_service
] = get_flight_search_service_dependency

app.dependency_overrides[
    booking_controller.get_room_booking_service
] = get_room_booking_service_dependency

app.dependency_overrides[
    auth_middleware_module.get_user_repo
] = get_user_repo_dependency

app.include_router(user_controller.router)
app.include_router(hotel_controller.router)
app.include_router(room_controller.router)
app.include_router(flight_controller.router)
app.include_router(booking_controller.router)

@app.on_event('startup')
def on_startup():
    """Создание таблиц при старте приложения."""
    print('Database tables check/creation...')
    create_db_and_tables()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("infrastructure.main:app", host="0.0.0.0", port=8000, reload=True)