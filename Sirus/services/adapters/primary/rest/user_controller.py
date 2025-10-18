from fastapi import APIRouter, Depends, HTTPException, status
from typing import Callable
from starlette.responses import JSONResponse

from services.core.domain.user import User
from services.core.usecases.user_management import UserManagementService

from services.infrastructure.security.auth_middleware import get_current_user
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

@router.post('/login', summary='Авторизация пользователя')
def login(
    # request: UserLoginRequest,
    request: UserLoginRequest,
    service: UserManagementService = Depends(get_user_management_service)
):
    """Возможность входа по почте и паролю. Устанавливает JWT в httponly cookie"""
    try:
        token = service.authenticate(
            email=request.email,
            password=request.password
        )

        response_data = {'access_token': token, 'token_type': 'bearer'}
        response = JSONResponse(content=response_data)

        response.set_cookie(
            key='access_token',
            value=token,
            httponly=True,
            samesite='lax',
            secure=False,
            max_age=3600 * 24 * 7
        )
        return response
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
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserManagementService = Depends(get_user_management_service)
):
    """Изменение информации о текущем аутентифицированном пользователе. Смена пароля требует текущий пароль"""

    update_data = request.model_dump(exclude_none=True)

    if not update_data or all(k.startswith('current') for k in update_data.keys()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Не переданы данные для обновления')
    
    try:
        updated_user = service.update_profile(current_user.user_id, update_data)
        return UserResponse.model_validate(updated_user)
    
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    