from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate

from api.auth_utils import check_allow_affect_user, decode_token, oauth2_scheme
from schemas.users import UpdateUserSchema, UserLoginHistorySchema, UserSchema
from services.auth import AuthService, get_auth_service
from services.exceptions import ConflictError, ObjectNotFoundError
from services.user import UserService, get_user_service

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Информация о пользователе",
    response_description="Полная информация о пользователе",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def get_user_info(
    user_id: UUID,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):

    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_allow_affect_user(payload, user_id)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        user = await user_service.get_user_by_id(user_id)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return user


@router.get(
    "/{user_id}/login_history",
    response_model=Page[UserLoginHistorySchema],
    summary="Информация об истории логинов пользователя",
    response_description="Список всех логинов пользователя с пагинацией",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def get_user_history(
    user_id: UUID,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_allow_affect_user(payload, user_id)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        user_history = await user_service.get_user_history(user_id)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return paginate(user_history)


@router.put(
    "/{user_id}",
    response_model=UpdateUserSchema,
    summary="Изменения данных пользователя",
    response_description="Актуальная информация о пользователе",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
        HTTPStatus.CONFLICT: {
            "description": "Ошибка при обновлении данных",
            "content": {
                "application/json": {
                    "example": {"detail": "user with this parameters already exists"}
                }
            },
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def put_user_info(
    user_id: UUID,
    request_data: UpdateUserSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_allow_affect_user(payload, user_id)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        user = await user_service.update_user(user_id, request_data)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")
    except ConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="user with this parameters already exists",
        )

    return user
