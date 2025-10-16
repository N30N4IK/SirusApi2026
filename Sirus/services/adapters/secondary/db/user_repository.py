import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.domain.user import User
from core.ports.out.user_repo import UserRepository
from infrastructure.database.models import UserORM
from infrastructure.database.connection import SessionLocal


class SQLAlchemyUserRepository(UserRepository):
    """РЕАЛИЗАЦИЯ РЕПОЗИТОРИЯ ПОЛЬЗОВАТЕЛЕЙ ЧЕРЕЗ SQLALCHEMY ORM"""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_session(self) -> Session:
        return self._session_factory()
    
    def _to_domain(self, orm_user: UserORM) -> User:
        """Преобразование orm-модели в доменную сущность"""
        return User(
            user_id=orm_user.user_id,
            email=orm_user.email,
            username=orm_user.username,
            password_hash=orm_user.password_hash,
            role=orm_user.role
        )

    def add(self, user: User) -> User:
        user.user_id = str(uuid.uuid4())
        orm_user = UserORM(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            password_hash=user.password_hash,
            role=user.role
        )
        try:
            with self._get_session() as session:
                session.add(orm_user)
                session.commit()
                session.refresh(orm_user)
            return self._to_domain(orm_user)
        except IntegrityError:
            '''Обработка ошибки, если email уже существует'''
            raise ValueError('Такой email уже есть')
        
    def get_by_email(self, email: str) -> Optional[User]:
        with self._get_session() as session:
            orm_user = session.query(UserORM).filter(UserORM.email == email).first()
            if orm_user:
                return self._to_domain(orm_user)
            return None
    
    def get_by_id(self, user: str) -> Optional[User]:
        with self._get_session() as session:
            orm_user = session.query(UserORM).filter(UserORM.user_id == id).first()
            if not orm_user:
                return "Пользователь не найден после обновления"
            

    def update(self, user: User) -> None:
        with self._get_session() as session:
            orm_user = session.query(UserORM).filter(UserORM.user_id == user.user_id).first()
            if not orm_user:
                raise ValueError('Не найден пользователь для обновления')
            
            orm_user.username = user.username

            session.commit()