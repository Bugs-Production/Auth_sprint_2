from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from fastapi_pagination.utils import disable_installed_extensions_check

from api.auth_utils import check_admin, decode_token, oauth2_scheme
from schemas.roles import RoleCreateSchema, RoleSchema
from services.auth import AuthService, get_auth_service
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.role import RoleService, get_role_service

router = APIRouter()

disable_installed_extensions_check()


@router.get(
    "/",
    response_model=Page[RoleSchema],
    summary="Список ролей",
    response_description="Список ролей",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешный запрос.",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "8f58b17c-283f-4177-9e89-50cbf060504d",
                                "title": "admin",
                            }
                        ]
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def roles(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> Page[RoleSchema]:

    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    check_admin(payload)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    roles_list = await role_service.get_roles_list()
    return paginate(roles_list)


@router.post(
    "/",
    response_model=RoleCreateSchema,
    summary="Создание новой роли",
    response_description="Подтверждение создания роли",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Конфликт с существующей ролью.",
            "content": {
                "application/json": {
                    "example": {"detail": "Role with title admin already exists."}
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации данных.",
            "content": {
                "application/json": {
                    "example": {"detail": "Input should be a valid string."}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Ошибка сервера при обработке запроса.",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
async def create_roles(
    role: RoleCreateSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> RoleSchema:

    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    check_admin(payload)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    try:
        new_role = await role_service.create_role(role)
        return new_role
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with title {role.title} already exists",
        )


@router.delete(
    "/{role_id}",
    summary="Удаление роли",
    response_description="Удаление роли по ee id",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешное удаление.",
            "content": {
                "application/json": {
                    "example": {"detail": "Role deleted successfully."}
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Отсутствие id у роли.",
            "content": {"application/json": {"example": {"detail": "Role not found."}}},
        },
    },
)
async def delete_roles(
    role_id: str,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> dict:

    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    check_admin(payload)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    try:
        await role_service.delete_role(role_id)
        return {"detail": "Role deleted successfully"}
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )


@router.put(
    "/{role_id}",
    response_model=RoleCreateSchema,
    summary="Обновление роли",
    response_description="Обновление роли по ee id",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешное изменение.",
            "content": {"application/json": {"example": {"detail": "string"}}},
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Отсутствие id у роли.",
            "content": {"application/json": {"example": {"detail": "Role not found."}}},
        },
    },
)
async def update_roles(
    role_id: str,
    role: RoleSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> RoleSchema:

    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    check_admin(payload)

    if not await auth_service.is_access_token_valid(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )

    try:
        updated_role = await role_service.change_role(role, role_id)
        return updated_role
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )
