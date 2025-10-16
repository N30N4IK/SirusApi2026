from enum import Enum
from dataclasses import dataclass

class Role(str, Enum):
    USER = 'user'
    ADMIN = 'admin'


@dataclass
class User:
    user_id: str
    email: str
    username: str
    password_hash: str
    role: Role = Role.USER