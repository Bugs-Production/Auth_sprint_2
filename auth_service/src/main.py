from contextlib import asynccontextmanager

import uvicorn
from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from starlette.middleware.sessions import SessionMiddleware

from api.v1 import admins, auth, oauth2, roles, users
from core import oauth_clients
from core.config import settings
from core.jaeger import configure_tracer
from db import postgres, redis
from middlewares.request_id_middleware import request_id_middleware
from middlewares.request_limit_middleware import check_request_limit


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
        postgres.engine = create_async_engine(
            postgres.dsn, echo=settings.engine_echo, future=True
        )
        postgres.async_session = async_sessionmaker(
            bind=postgres.engine, expire_on_commit=False, class_=AsyncSession
        )
        oauth_clients.google_client = AsyncOAuth2Client(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            redirect_uri=settings.google_redirect_url,
            scope="openid email profile",
        )
        yield
    finally:
        await redis.redis.aclose()
        await oauth_clients.google_client.aclose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/auth/api/openapi/",
    openapi_url="/auth/api/openapi.json",
    default_response_class=ORJSONResponse,
)

# для трассировки Jaeger
configure_tracer()
FastAPIInstrumentor.instrument_app(app)
app.middleware("http")(request_id_middleware)

# для лимита запросов
app.middleware("http")(check_request_limit)
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret_key)

app.include_router(roles.router, prefix="/auth/api/v1/roles", tags=["roles"])
app.include_router(users.router, prefix="/auth/api/v1/users", tags=["users"])
app.include_router(admins.router, prefix="/auth/api/v1/users", tags=["admins"])
app.include_router(auth.router, prefix="/auth/api/v1/auth", tags=["auth"])
app.include_router(oauth2.router, prefix="/auth/api/v1/oauth", tags=["oauth2"])

add_pagination(app)
