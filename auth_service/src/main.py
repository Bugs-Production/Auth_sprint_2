from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from api.v1 import admins, auth, roles, users
from core.config import settings
from db import postgres, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
        postgres.engine = create_async_engine(postgres.dsn, echo=settings.engine_echo, future=True)
        postgres.async_session = async_sessionmaker(
            bind=postgres.engine, expire_on_commit=False, class_=AsyncSession
        )
        yield
    finally:
        await redis.redis.aclose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(admins.router, prefix="/api/v1/users", tags=["admins"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

add_pagination(app)
