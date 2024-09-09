from http import HTTPStatus
from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from core.config import JWT_ALGORITHM, settings

# Для чтения access-токенов из заголовка запроса
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.exceptions.InvalidTokenError:
        return None

    return payload


def check_allow_affect_user(auth_data: dict[str, Any], user_id: UUID):
    """
    Операции может производить только admin или пользователь со своим профилем
    """
    if "admin" not in auth_data["roles"] and str(user_id) != auth_data["user_id"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)


def check_admin(auth_data: dict[str, Any]):
    """Проверяет что только админ может получить доступ к endpoints"""
    if "admin" not in auth_data["roles"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
