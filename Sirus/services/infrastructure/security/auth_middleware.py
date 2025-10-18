from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer

from services.core.domain.user import User, Role
from services.core.ports.out.user_repo import UserRepository
from services.infrastructure.security.password import verify_password

SECRET_KEY = '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login', auto_error=False)

def create_access_token(user_id: str, role: Role):
    """Генерация jwt токена"""
    to_encode = {'sub': user_id, 'role': role.value}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_token_from_cookie(request: Request) -> Optional[str]:
    """Извлекает токен из cookie, если он там есть"""
    return request.cookies.get('access_token')

def get_user_repo() -> UserRepository:
    """Заглушка"""
    raise NotImplementedError

def get_current_user(request: Request,
                     token_header: Optional[str] = Depends(oauth2_scheme),
                     repo: UserRepository = Depends(get_user_repo)) -> User:
    """Извлекает и валидириует текущего аутентифицированного пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    token = token_header
    if token is None:
        token = get_token_from_cookie(request)

    if token is None:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError as e:
        raise credentials_exception
    except Exception as e:
        raise credentials_exception
    
    user = repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

def admin_required(user: User = Depends(get_current_user)) -> User:
    """Проверка, что пользователь имеет роль admin"""
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Требуются права администратора'
        )
    
    return user