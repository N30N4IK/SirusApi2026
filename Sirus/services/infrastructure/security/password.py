from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

MAX_PASSWORD_LENGTH_BYTES = 72

def hash_password(password: str) -> str:
    """ХЭШИРОВАНИЕ ПАРОЛЯ"""
    safe_password = password.encode('utf-8')[:MAX_PASSWORD_LENGTH_BYTES]
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ПРОВЕРКА СООТВЕТСТВИЯ ОТКРЫТОГО ПАРОЛЯ ХЭШУ"""
    safe_password = plain_password.encode('utf-8')[:MAX_PASSWORD_LENGTH_BYTES]
    return pwd_context.verify(safe_password, hashed_password)