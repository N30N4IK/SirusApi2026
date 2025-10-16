from pydantic import BaseModel, EmailStr, field_validator
from core.domain.user import Role

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль минимум 8 символов')
        if len(v) > 72:
            raise ValueError('Пароль максимум 72 символа')
        return v
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class UserUpdateRequest(BaseModel):
    new_username: str

class UserResponse(BaseModel):
    """Схема отправки данных пользователю клиенту"""
    user_id: str
    email: EmailStr
    username: str
    role: Role

    class Config:
        from_attributes = True