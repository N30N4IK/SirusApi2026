from services.infrastructure.security.auth_middleware import create_access_token
from services.infrastructure.security.password import hash_password, verify_password
from services.core.ports.out.user_repo import UserRepository
from services.core.domain.user import User, Role

from typing import Dict, Any


class UserManagementService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
    
    def register_user(self, email, username, password) -> User:
        if self._user_repo.get_by_email(email):
            raise ValueError('Пользвоатель с такой почтой уже существует')

        hashed_password = hash_password(password)

        new_user = User(
            user_id=None,
            email=email,
            username=username,
            password_hash=hashed_password,
            role=Role.USER
        )
        return self._user_repo.add(new_user)
    
    def authenticate(self, email: str, password: str) -> str:
        user = self._user_repo.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise ValueError('Неверный email или пароль')

        return create_access_token(user.user_id, user.role)
    
    def update_profile(self, user_id: str, data: Dict[str, Any]) -> User:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('Пользователь не найден')
        
        if 'new_password' in data:
            current_password = data.get("current_password")

            if not current_password:
                raise PermissionError('Для смены пароля требуется ввести текущий пароль')
            
            if not verify_password(current_password, user.password_hash):
                raise PermissionError('Неверный текущий пароль')
            
            user.password_hash = hash_password(data['new_password'])

        if 'new_username' in data:
            user.username = data['new_username']
        
        if 'new_email' in data:
            if self._user_repo.get_by_email(data['new_email']):
                raise ValueError("Email уже используется другим аккаунтом")
            user.email = data['new_email']

        if 'current_password' in data:
            del data['current_password']

            self._user_repo.update(user)
            return user