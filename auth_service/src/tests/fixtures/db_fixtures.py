import uuid
from datetime import datetime, timedelta

import jwt
import pytest
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import NullPool

from core.config import JWT_ALGORITHM, settings
from db.postgres import Base, get_postgres_session
from main import app
from models import LoginHistory, RefreshToken, Role, User
from tests import constants

DATABASE_URL_TEST = settings.postgres_url

# Database setup

engine_test = create_async_engine(
    DATABASE_URL_TEST, poolclass=NullPool, echo=settings.engine_echo
)
async_session_maker = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)

metadata = Base.metadata
metadata.bind = engine_test


async def override_get_async_session():
    yield async_session_maker


app.dependency_overrides[get_postgres_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="function")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


# Data for tests


@pytest.fixture(scope="function")
async def admin():
    # Создание роли админа
    async with async_session_maker() as session:
        admin_role = Role(
            id=constants.ROLE_ADMIN_UUID, title=constants.ROLE_ADMIN_TITLE
        )
        session.add(admin_role)
        await session.commit()

        # Создание пользователя-админа
        admin_user = User(
            login=constants.ADMIN_LOGIN,
            password=constants.ADMIN_PASSWORD,
            first_name="Admin",
            last_name="User",
        )
        admin_user.id = constants.ADMIN_UUID
        admin_user.roles.append(admin_role)
        session.add(admin_user)
        await session.commit()

    return admin_user


@pytest.fixture(scope="function")
async def access_token_admin(admin):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(admin.id),
        "exp": int(valid_till.timestamp()),
        "roles": ["admin"],
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
async def moderator():
    # Создание роли модератора
    async with async_session_maker() as session:
        moderator_role = Role(id=uuid.uuid4(), title="moderator")
        session.add(moderator_role)
        await session.commit()

        # Создание пользователя-модератора
        moderator = User(
            login=constants.MODERATOR_LOGIN,
            password=constants.MODERATOR_PASSWORD,
            first_name="Moderator",
            last_name="Bla",
        )
        moderator.id = constants.MODERATOR_UUID
        moderator.roles.append(moderator_role)
        session.add(moderator)
        await session.commit()

    return moderator


@pytest.fixture(scope="function")
async def access_token_moderator(moderator):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(moderator.id),
        "exp": int(valid_till.timestamp()),
        "roles": ["moderator"],
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return token


@pytest.fixture(scope="function")
async def refresh_token_moderator(moderator):
    valid_till = datetime.now() + timedelta(hours=1)
    payload = {
        "user_id": str(moderator.id),
        "exp": int(valid_till.timestamp()),
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)

    async with async_session_maker() as session:
        refresh = RefreshToken(
            user_id=moderator.id,
            expires_at=valid_till,
            token=token,
        )
        session.add(refresh)
        await session.commit()

    return token


@pytest.fixture(scope="function")
async def role():
    # создание роли для тестов
    async with async_session_maker() as session:
        new_role = Role(id=constants.TEST_ROLE_UUID, title="new role")
        session.add(new_role)
        await session.commit()

        return new_role


@pytest.fixture(scope="function")
async def create_multiple_roles():
    async with async_session_maker() as session:
        roles = [Role(id=uuid.uuid4(), title=f"role_{i}") for i in range(1, 11)]
        session.add_all(roles)
        await session.commit()
        return roles


@pytest.fixture(scope="function")
async def add_test_role_to_moderator(moderator, role):
    async with async_session_maker() as session:
        moderator.roles.append(role)
        session.add(moderator)
        await session.commit()


# Фикстура для заголовков авторизации администратора
@pytest.fixture(scope="function")
def headers_admin(access_token_admin):
    return {"Authorization": f"Bearer {access_token_admin}"}


# Фикстура для заголовков авторизации модератора
@pytest.fixture(scope="function")
def headers_moderator(access_token_moderator):
    return {"Authorization": f"Bearer {access_token_moderator}"}


# Фикстура для заголовков авторизации с невалидным access_token админа
@pytest.fixture(scope="function")
def headers_admin_invalid(access_token_admin):
    wrong_access_token = access_token_admin[::-1]
    return {"Authorization": f"Bearer {wrong_access_token}"}


@pytest.fixture(scope="function")
async def login_multiple_times(moderator):
    async with async_session_maker() as session:
        login_history = [
            LoginHistory(
                user_id=moderator.id,
                event_date=datetime.now() - timedelta(days=i),
                success=True,
            )
            for i in range(0, 5)
        ]

        session.add_all(login_history)
        await session.commit()

        return login_history
