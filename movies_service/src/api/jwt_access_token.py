import http
import time
from enum import Enum
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from core.config import settings


class ExpiredTokenException(Exception):
    pass


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict | None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            # TODO: реализовать логику перенаправления в сервис аутентификации для обновления токена
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[dict]:
        return decode_token(jwt_token)


security_jwt = JWTBearer()


class RolesChoices(Enum):
    SUBSCRIBER = "subscriber"
    ADMIN = "admin"


class FilmsPermissionChoices(Enum):
    FREE = "FR"
    PREMIUM = "PR"


async def get_permissions(user: dict) -> str:
    # при регистрации в сервисе пользователь создается без роли ["без подписок"],
    # в таком случае ему доступны только фильмы с полем viewing_permission=FR,
    # admin, subscriber могут видеть все фильмы с полем viewing_permission=PR

    # TODO: чот не красивая логика, тк фильмы помеченные FR не будут отображаться для всех
    # кажется нужно сделать viewing_permission не text, а list
    roles = user.get("roles", [])
    if not roles:
        return FilmsPermissionChoices.FREE.value
    return FilmsPermissionChoices.PREMIUM.value
