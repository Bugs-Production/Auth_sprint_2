from sqlalchemy import select
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from werkzeug.security import generate_password_hash

from core.config import settings
from db import postgres
from models.roles import Role
from models.user import User


async def create_superuser(login: str, password: str, first_name: str, last_name: str):
    engine = create_async_engine(postgres.dsn, echo=settings.engine_echo, future=True)
    async_session = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        hashed_password = generate_password_hash(password)
        role = await get_admin_role(session)
        superuser = User(
            login=login,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        superuser.roles.append(role)
        session.add(superuser)
        await session.commit()


async def get_admin_role(session: AsyncSession):
    stmt = select(Role).filter_by(title="admin")
    result = await session.scalars(stmt)
    role = result.one_or_none()
    if not role:
        role = Role(title="admin")
        session.add(role)
        await session.commit()
        await session.refresh(role)
    return role
