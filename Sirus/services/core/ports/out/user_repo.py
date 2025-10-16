from abc import ABC, abstractmethod
from typing import Optional
from core.domain.user import User

class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def update(self, user: User) -> None: ...
    