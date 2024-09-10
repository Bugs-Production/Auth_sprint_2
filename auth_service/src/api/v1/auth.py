from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.auth_utils import decode_token
from schemas.auths import (AuthOutputSchema, LoginInputSchema,
                           RefreshInputSchema)
from schemas.users import CreateUserSchema
from services.auth import AuthService, get_auth_service
from services.exceptions import ConflictError, ObjectNotFoundError
from services.user import UserService, get_user_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthOutputSchema,
    summary="Регистрация пользователя",
    response_description="Пара токенов: access, refresh",
    responses={
        HTTPStatus.CONFLICT: {
            "description": "Пользователь с такими параметрами уже существует",
            "content": {
                "application/json": {
                    "example": {"detail": "user with this parameters already exists"}
                }
            },
        },
    },
)
async def signup(
    user_data: CreateUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthOutputSchema:
    try:
        user = await user_service.create_user(user_data)
    except ConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="user with this parameters already exists",
        )

    user_id = str(user.id)
    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

    access_token = await auth_service.generate_access_token(user_id, user_roles)
    refresh_token = await auth_service.emit_refresh_token(user_id)

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=AuthOutputSchema,
    summary="Обновление access token",
    response_description="Пара токенов: access, refresh",
    responses={
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
async def refresh(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthOutputSchema:

    refresh_token_data = decode_token(request_data.refresh_token)
    if not refresh_token_data:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    if not await auth_service.is_refresh_token_valid(request_data.refresh_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    access_token_data = decode_token(request_data.access_token)
    if access_token_data:
        await auth_service.invalidate_access_token(request_data.access_token)

    user_id = refresh_token_data["user_id"]

    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]
    refresh_token, access_token = await auth_service.update_refresh_token(
        user_id,
        request_data.refresh_token,
        user_roles,
    )

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/login",
    response_model=AuthOutputSchema,
    summary="Вход пользователя в аккаунт",
    response_description="Пара токенов: access, refresh",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "user with this parameters already exists"}
                }
            },
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Ошибка валидации пароля",
            "content": {
                "application/json": {"example": {"detail": "invalid password"}}
            },
        },
    },
)
async def login(
    login_data: LoginInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> AuthOutputSchema:
    try:
        user = await user_service.get_user_by_login(login_data.login)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    if not user.check_password(login_data.password):
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="invalid password")

    user_id = str(user.id)

    await user_service.save_login_history(user_id)

    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

    access_token = await auth_service.generate_access_token(user_id, user_roles)
    refresh_token = await auth_service.emit_refresh_token(user_id)

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    status_code=200,
    summary="Выход пользователя из аккаунта",
    response_description="",
    responses={
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
    },
)
async def logout(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token_data = decode_token(request_data.refresh_token)
    if not refresh_token_data:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    await auth_service.invalidate_refresh_token(request_data.refresh_token)

    if decode_token(request_data.access_token):
        await auth_service.invalidate_access_token(request_data.access_token)

    return {"detail": "logout success"}


@router.post(
    "/logout/all",
    status_code=200,
    summary="Выход пользователя из остальных аккаунтов",
    response_description="",
    responses={
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
    },
)
async def logout_all(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token_data = decode_token(request_data.refresh_token)
    if not refresh_token_data:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    await auth_service.invalidate_user_refresh_tokens(
        refresh_token_data["user_id"], request_data.refresh_token
    )
    return {"detail": "logout from all other devices success"}
