from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.postgres import get_postgres_session
from models.roles import Role
from models.user import User
from services.exceptions import (ConflictError, ObjectNotFoundError,
                                 UserNotFoundError)


class AdminService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_user_roles(self, user_id: UUID):
        async with self.postgres_session() as session:
            user_scalars = await session.scalars(select(User).where(User.id == user_id))
            user = user_scalars.first()
            if not user:
                raise UserNotFoundError

            role_scalars = await session.scalars(
                select(Role).join(User.roles).where(User.id == user_id)
            )
            roles = role_scalars.fetchall()
            if not roles:
                raise ObjectNotFoundError
            return roles

    async def add_user_role(self, user_id: UUID, role_id: UUID):
        async with self.postgres_session() as session:
            role_scalars = await session.scalars(select(Role).where(Role.id == role_id))
            role = role_scalars.first()
            if not role:
                raise ObjectNotFoundError

            user_scalars = await session.scalars(
                select(User).options(selectinload(User.roles)).where(User.id == user_id)
            )
            user = user_scalars.first()
            if not user:
                raise UserNotFoundError

            user.roles.append(role)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError
            return role

    async def remove_user_role(self, user_id: UUID, role_id: UUID):
        async with self.postgres_session() as session:
            user_scalars = await session.scalars(
                select(User).options(selectinload(User.roles)).where(User.id == user_id)
            )
            user = user_scalars.first()
            if not user:
                raise UserNotFoundError

            role_scalars = await session.scalars(select(Role).where(Role.id == role_id))
            role = role_scalars.first()
            if not role:
                raise ObjectNotFoundError

            if role in user.roles:
                user.roles.remove(role)

            await session.commit()
            return role


@lru_cache()
def get_admin_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> AdminService:
    return AdminService(postgres_session)
