from fastapi import FastAPI, Depends
from adapter.primary.rest import user_controller
from core.usecases.user_management import UserManagementService
from adapter.secondary.db.user_repository import SSQLAlchemyUserRepository
from infrastructure.database.connection import SessionLocal, create_db_and_tables
from infrastructure.security.auth_middleware import get_user_repo

import infrastructure.security.auth_middleware

user_repository_instance = SSQLAlchemyUserRepository(session_factory=SessionLocal)

user_management_service_instance = UserManagementService(
    user_repo=user_repository_instance
)


def get_user_management_service_dependency() -> UserManagementService:
    """DI для use case (в контроллеры)"""
    return user_management_service_instance

def get_user_repo_dependency() -> SSQLAlchemyUserRepository:
    """Di для репозитория (в auth_middleware)"""
    return user_repository_instance


app = FastAPI(title='Booking aggregator API')

app.dependency_overrides[user_controller.get_user_management_service] = get_user_management_service_dependency

app.dependency_overrides[infrastructure.security.auth_middleware.get_user_repo] = get_user_repo_dependency

app.include_router(user_controller.router)


@app.on_event('startup')
def on_startup():
    """Создание таблиц при старте приложения"""
    print('Database tables check/creation...')
    create_db_and_tables()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)