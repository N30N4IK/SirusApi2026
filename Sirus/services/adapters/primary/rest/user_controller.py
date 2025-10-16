from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Callable

from core.domain.user import User
from core.usecases.user_management import UserManagementService

from infrastructure.security.auth_middleware import get_current_user
from .user_schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    TokenResponse
)

router = APIRouter(prefix='/users', tags=['Users'])


def get_user_management_service() -> UserManagementService:
    """Placeholder для получения сервиса управления пользователями"""
    raise NotImplementedError


@router.post(
    '/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя'
)
def register(
    request: UserRegistrationRequest,
    service: UserManagementService = Depends(get_user_management_service)
):
    """
    Регистрация с вводом имени, почты и пароля.
    Роль по умолчанию 'user'
    """
    try:
        user = service.register_user(
            email=request.email,
            username=request.username,
            password=request.password
        )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post('/login', response_model=TokenResponse, summary='Авторизация пользователя')
def login(
    # request: UserLoginRequest,
    request: OAuth2PasswordRequestForm = Depends(),
    service: UserManagementService = Depends(get_user_management_service)
):
    """Возможность входа по почте и паролю. Возвращает JWT токен"""
    try:
        token = service.authenticate(
            email=request.username,
            password=request.password
        )
        return TokenResponse(access_token=token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e), headers={'WWW-Authenticate': 'Bearer'})
    
@router.get('/me', response_model=UserResponse, summary='Получить информацию о себе')
def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем аутентифицированном пользователе"""
    return UserResponse.model_validate(current_user)


@router.put('/update', response_model=UserResponse, summary='Изменить информацию о себе')
def update_users_me(
    current_user: User = Depends(get_current_user)
):
    """Изменение информации о текущем аутентифицированном пользователе"""
    