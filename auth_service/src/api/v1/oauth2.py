from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from schemas.auths import AuthOutputSchema
from services.auth import AuthService, get_auth_service
from services.exceptions import OAuthUserNotFoundError, ObjectNotFoundError
from services.oauth2 import OAuthServiceGoogle, get_google_service

router = APIRouter()


@router.get(
    "/",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Вход в сервис через OAuth провайдера",
    responses={
        status.HTTP_307_TEMPORARY_REDIRECT: {
            "description": "Перенаправление пользователя на авторизацию в сервисе",
        }
    },
)
async def main_page(
    google_service: OAuthServiceGoogle = Depends(get_google_service),
) -> RedirectResponse:
    # Так как oauth2 только для аутентификации, нам нужно сгенерировать
    # для клиента url в нашем сервисе для авторизации.
    url = await google_service.create_redirect_url()
    return RedirectResponse(url)


@router.get(
    "/auth",
    response_model=AuthOutputSchema,
    summary="Авторизация клиента в сервисе",
    response_description="Пара токенов: access, refresh",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Ошибки связанные с запросами к OAuth провайдеру",
            "content": {"application/json": {"example": {"detail": "error"}}},
        },
    },
)
async def auth2(
    request: Request,
    google_service: OAuthServiceGoogle = Depends(get_google_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    code = request.query_params.get("code")
    access_token_to_provider = await google_service.get_access_token_from_provider(code)

    user_data = await google_service.get_user_data_from_provider(
        access_token_to_provider
    )

    user_agent = request.headers.get("user-agent", "Unknown")
    service_user = await google_service.authorize_user(user_data, user_agent)

    user_id = str(service_user.id)
    access_token = await auth_service.generate_access_token(user_id, [])
    refresh_token = await auth_service.emit_refresh_token(user_id)

    return AuthOutputSchema(
        access_token=access_token, refresh_token=refresh_token, user_id=user_id
    )


@router.delete(
    "/{login}",
    status_code=200,
    summary="Открепить social аккаунт от личного кабинета",
    response_description="Открепить social аккаунт по логину в сервисе",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Не найден пользователь или social аккаунт",
            "content": {"application/json": {"example": {"detail": "error"}}},
        }
    },
)
async def delete_oauth_user(
    login: str,
    google_service: OAuthServiceGoogle = Depends(get_google_service),
):
    try:
        await google_service.delete_oauth_account(login)
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user by login not found",
        )
    except OAuthUserNotFoundError:
        return {"detail": "social account already deleted"}

    return {"detail": "social account successfully deleted"}
