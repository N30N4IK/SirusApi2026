from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer

from core.domain.user import User, Role
from core.ports.out.user_repo import UserRepository
from infrastructure.security.password import verify_password

SECRET_KEY = 'e921af50f1ebbb7597aec386bf753ec5bbe3161da56ff5a9'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login', auto_error=False)

def create_access_token(user_id: str, role: Role):
    """Генерация jwt токена"""
    to_encode = {'sub': user_id, 'role': role.value}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# token: str = Depends(oauth2_scheme)

def get_user_repo() -> UserRepository:
    """Заглушка"""
    raise NotImplementedError

def get_current_user(token: Optional[str] = Depends(oauth2_scheme),
                     repo: UserRepository = Depends(get_user_repo)) -> User:
    """Извлекает и валидириует текущего аутентифицированного пользователя"""
    print(f"--- DEBUG: get_current_user CALLED. Token start: {token}...") 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid authentication credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    if token is None:
        print(f'--- DEBUG get_current_user CALLED. Token: {token}')
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('sub')
        print(f'Decoded User ID: {user_id}')
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError as e:
        print(f'JWT error: {e}')
        raise credentials_exception
    except Exception as e:
        print(f'Unexpected error in get_current_user: {e}')
        raise credentials_exception
    
    user = repo.get_by_id(user_id)
    print(f'Found user: {user}')
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