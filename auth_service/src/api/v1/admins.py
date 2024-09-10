from http import HTTPStatus
from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from api.auth_utils import (check_admin, check_allow_affect_user, decode_token,
                            oauth2_scheme)
from schemas.roles import RoleSchema, RoleUpdateSchema
from services.admin import AdminService, get_admin_service
from services.auth import AuthService, get_auth_service
from services.exceptions import (ConflictError, ObjectNotFoundError,
                                 UserNotFoundError)

router = APIRouter()


@router.get(
    "/{user_id}/roles",
    response_model=Union[Page[RoleSchema], list],
    summary="Информация по ролям пользователя",
    response_description="Информация по ролям пользователя",
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
async def get_user_roles(
    user_id: UUID,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
    params: Params = Depends(),
) -> Union[Page[RoleSchema], list]:
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_allow_affect_user(payload, user_id)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        roles = await admin_service.get_user_roles(user_id)
        return paginate(roles, params)
    except ObjectNotFoundError:
        return []
    except UserNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="user does not exist"
        )


@router.post(
    "/{user_id}/roles",
    response_model=RoleSchema,
    summary="Добавление новой роли пользователю",
    response_description="Информация по добавленной роли пользователю",
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
async def add_user_role(
    user_id: UUID,
    request_data: RoleUpdateSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
) -> RoleSchema:
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_admin(payload)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        role_id = request_data.role_id
        role = await admin_service.add_user_role(user_id, role_id)
        return role
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="role not found")
    except UserNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="user does not exist"
        )
    except ConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="user already has this role"
        )


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=RoleSchema,
    summary="Удаление роли у пользователя",
    response_description="Информация по удалённой роли пользователю",
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
async def remove_user_role(
    user_id: UUID,
    role_id: UUID,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
) -> RoleUpdateSchema:
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_admin(payload)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        role = await admin_service.remove_user_role(user_id, role_id)
        return role
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="role not found")
    except UserNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="user does not exist"
        )
