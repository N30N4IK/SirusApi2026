from infrastructure.security.auth_middleware import create_access_token
from infrastructure.security.password import hash_password, verify_password
from core.ports.out.user_repo import UserRepository
from core.domain.user import User, Role


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
    
    def update_username(self, user_id: str, new_username: str) -> User:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('Пользователь не найден')

        user.username = new_username
        self._user_repo.update(user)
        return user