import sys
import os
import getpass
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

Sirus = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(Sirus)


from services.infrastructure.database.connection import create_db_and_tables, SessionLocal
from services.infrastructure.database.models import UserORM
from services.core.usecases.user_management import UserManagementService
from services.adapters.secondary.db.user_repository import SQLAlchemyUserRepository
from services.core.domain.user import Role
from services.infrastructure.security.password import hash_password

USER_REPO = SQLAlchemyUserRepository(session_factory=SessionLocal)
USER_SERVICE = UserManagementService(user_repo=USER_REPO)

def create_initial_admin(session: Session):
    """Создание первого пользователя с ролью ADMIN, если его не существует"""

    ADMIN_EMAIL = 'admin@booking.com'
    ADMIN_USERNAME = 'Admin'

    existing_admin = session.query(UserORM).filter(UserORM.email == ADMIN_EMAIL).first()
    if existing_admin:
        if existing_admin.role == Role.ADMIN:
            print(f'Администратор с email: {ADMIN_EMAIL} уже существует')
            return
        
    print(f'Создание учетной записи Админа')

    while True:
        try: 
            password = getpass.getpass('Введите пароль для админа (отображаться пароль не будет из-за getpass): ')
            if len(password) < 8:
                print('Пароль слишком короткий (Минимум 8 символов)')
                continue
            break
        except EOFError:
            print('\nОшибка ввода пароля')
            return
        
    
    try:
        hashed_password = hash_password(password)

        from services.core.domain.user import User

        if existing_admin:
            existing_admin.password_hash = hashed_password
            existing_admin.role = Role.ADMIN
            session.add(existing_admin)
            session.commit()
            print('Учетная запись обновлена до ADMIN')
        else:
            new_admin = User(
                user_id=None,
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                password_hash=hashed_password,
                role=Role.ADMIN
            )
            print(f'Администратор: {new_admin}')
            USER_REPO.add(new_admin)
            print(f'Администратор "{ADMIN_USERNAME}" успешно создан')
        
    except IntegrityError:
        session.rollback()
        print('Ошибка: Пользователь с таким email уже существует')
    except Exception as e:
        print(f'Ошибка при создании Админа: {e}')

def main():
    print('--- Инициализация базы данных ---')

    create_db_and_tables()
    print('Таблицы БД успешно созданы или проверены')

    try:
        with SessionLocal() as session:
            create_initial_admin(session)
    except Exception as e:
        print(f'Критическая ошибка инициализации: {e}')

    print('--- Инициализация завершена ---')

if __name__ == '__main__':
    main()