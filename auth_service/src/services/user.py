from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models as db_models
from db.postgres import get_postgres_session
from schemas.users import CreateUserSchema, UpdateUserSchema
from services.exceptions import ConflictError, ObjectNotFoundError


class UserService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_user_by_id(self, user_id: UUID) -> db_models.User:
        async with self.postgres_session() as session:
            user = await session.get(db_models.User, user_id)
            if not user:
                raise ObjectNotFoundError

            return user

    async def get_user_by_login(self, login: str) -> db_models.User:
        async with self.postgres_session() as session:
            results = await session.execute(
                select(db_models.User).filter_by(login=login)
            )
            user = results.scalars().first()
            if not user:
                raise ObjectNotFoundError

            return user

    async def update_user(
        self, user_id: UUID, user_data: UpdateUserSchema
    ) -> db_models.User:
        async with self.postgres_session() as session:
            user = await session.get(db_models.User, user_id)

            if not user:
                raise ObjectNotFoundError

            for field in user_data.model_fields_set:
                val = getattr(user_data, field)
                setattr(user, field, val)

            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError

            return user

    async def get_user_history(self, user_id: UUID) -> list[db_models.LoginHistory]:
        async with self.postgres_session() as session:
            results = await session.execute(
                select(db_models.User)
                .where(db_models.User.id == user_id)
                .options(selectinload(db_models.User.login_history))
            )

            user = results.scalars().first()
            if not user:
                raise ObjectNotFoundError

            login_history = user.login_history

            return login_history

    async def create_user(self, user_data: CreateUserSchema) -> db_models.User:
        async with self.postgres_session() as session:
            user = db_models.User(
                login=user_data.login,
                password=user_data.password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError

            return user

    async def get_user_roles(self, user_id: str) -> list[db_models.Role]:
        async with self.postgres_session() as session:
            results = await session.execute(
                select(db_models.User)
                .where(db_models.User.id == user_id)
                .options(selectinload(db_models.User.roles))
            )
            if not results:
                raise ObjectNotFoundError

            user = results.scalars().first()

            user_roles = user.roles
            return user_roles

    async def save_login_history(self, user_id) -> None:
        async with self.postgres_session() as session:
            login_history = db_models.LoginHistory(
                user_id=user_id,
                success=True,
            )
            session.add(login_history)
            await session.commit()


@lru_cache()
def get_user_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> UserService:
    return UserService(postgres_session)
