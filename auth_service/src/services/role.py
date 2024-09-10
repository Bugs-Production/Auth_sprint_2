from abc import ABC, abstractmethod
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import get_postgres_session
from models.roles import Role
from schemas.roles import RoleCreateSchema, RoleSchema
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)


class AbstractRoleService(ABC):
    @abstractmethod
    async def get_roles_list(self) -> Role | None:
        pass

    @abstractmethod
    async def create_role(self, role: RoleCreateSchema) -> Role:
        pass

    @abstractmethod
    async def delete_role(self, role_id: str) -> None:
        pass

    @abstractmethod
    async def change_role(self, role: RoleCreateSchema, role_id: str) -> Role:
        pass

    @abstractmethod
    async def get_role_by_id(self, role_id: str) -> Role:
        pass


class RoleService(AbstractRoleService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_role_by_id(self, role_id: str) -> Role:
        """Поиск роли по id"""
        async with self.postgres_session() as session:
            result = await session.scalars(select(Role).filter_by(id=role_id))
            return result.first()

    async def get_roles_list(self) -> Role | None:
        """Получение всех ролей"""
        async with self.postgres_session() as session:
            result = await session.scalars(select(Role))
            return result.all()

    async def create_role(self, role: RoleCreateSchema) -> Role | HTTPException:
        """Создание роли"""
        new_role = Role(title=role.title)

        async with self.postgres_session() as session:
            try:
                session.add(new_role)
                await session.commit()
                await session.refresh(new_role)
                return new_role
            except IntegrityError:
                raise ObjectAlreadyExistsException

    async def delete_role(self, role_id: str) -> None:
        """Удаление роли"""
        role = await self.get_role_by_id(role_id)

        if role is None:
            raise ObjectNotFoundError

        async with self.postgres_session() as session:
            await session.delete(role)
            await session.commit()

    async def change_role(
        self, role: RoleCreateSchema, role_id: str
    ) -> Role | HTTPException:
        """Изменение роли"""
        old_role = await self.get_role_by_id(role_id)

        if old_role is None:
            raise ObjectNotFoundError

        if old_role.title == role.title:
            return old_role

        old_role.title = role.title

        async with self.postgres_session() as session:
            session.add(old_role)
            await session.commit()
            await session.refresh(old_role)

            return old_role


@lru_cache()
def get_role_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> RoleService:
    return RoleService(postgres_session)
