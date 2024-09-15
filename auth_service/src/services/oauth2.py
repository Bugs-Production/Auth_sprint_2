import random
import string
from abc import ABC, abstractmethod
from functools import lru_cache

import requests
from authlib.integrations.base_client.errors import OAuthError
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models as db_models
from core import oauth_clients
from core.config import settings
from db.postgres import get_postgres_session
from schemas.auths import AuthOutputSchema, OAuthUser
from schemas.users import CreateUserSchema
from services.exceptions import OAuthUserNotFoundError, ObjectNotFoundError
from services.user import UserService, get_user_service


class AbstractOAuthService(ABC):
    @abstractmethod
    async def create_redirect_url(self) -> str:
        pass

    @abstractmethod
    async def get_access_token_from_provider(self, *args, **kwargs) -> str:
        pass

    @abstractmethod
    async def get_user_data_from_provider(self, *args, **kwargs) -> OAuthUser:
        pass

    @abstractmethod
    async def authorize_user(self, *args, **kwargs) -> AuthOutputSchema:
        pass

    @abstractmethod
    async def delete_oauth_account(self, *args, **kwargs) -> None:
        pass


class OAuthServiceGoogle(AbstractOAuthService):
    def __init__(self, postgres_session: AsyncSession, user_service: UserService):
        self.postgres_session = postgres_session
        self.user_service = user_service

    provider_name = "Google"

    @staticmethod
    def _generate_random_password(length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(characters) for _ in range(length))
        return password

    @staticmethod
    async def create_redirect_url() -> str:
        uri, _state = oauth_clients.google_client.create_authorization_url(
            url=settings.google_base_url
        )
        return uri

    @staticmethod
    async def get_access_token_from_provider(code: str) -> str:
        try:
            data: dict = await oauth_clients.google_client.fetch_token(
                settings.google_token_url,
                authorization_response=code,
                code=code,
                grant_type="authorization_code",
            )
        except OAuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"error while connect to redirect url: {exc!s}",
            )

        return data.get("access_token")

    async def get_user_data_from_provider(self, access_token: str) -> OAuthUser:
        headers = {"Authorization": f"Bearer {access_token}"}
        result = requests.get(settings.google_userinfo_url, headers=headers)
        if result.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="failed to get user info from provider",
            )
        user_data = result.json()

        return OAuthUser(
            oauth_user_id=user_data.get("id"),
            email=user_data.get("email"),
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name"),
            provider_type=self.provider_name,
        )

    async def get_oauth_user_from_db(self, oauth_user_id: str) -> OAuthUser:
        async with self.postgres_session() as session:
            user_scalars = await session.scalars(
                select(db_models.OAuthAccount).where(
                    db_models.OAuthAccount.oauth_user_id == oauth_user_id,
                    db_models.OAuthAccount.provider_type == self.provider_name,
                )
            )
            user = user_scalars.first()

            return user if user else None

    async def create_oauth_user(
        self, oauth_user: OAuthUser, service_user_id: str
    ) -> db_models.OAuthAccount:
        async with self.postgres_session() as session:
            user = db_models.OAuthAccount(
                user_id=service_user_id,
                oauth_user_id=str(oauth_user.oauth_user_id),
                provider_type=self.provider_name,
            )
            session.add(user)
            await session.commit()

            return user

    async def authorize_user(
        self, user_data: OAuthUser, user_agent: str
    ) -> AuthOutputSchema:
        oauth_user_db = await self.get_oauth_user_from_db(user_data.oauth_user_id)

        if oauth_user_db:
            try:
                service_user = await self.user_service.get_user_by_id(
                    oauth_user_db.user_id
                )
            except ObjectNotFoundError:
                pass
            else:
                # Есть oauth_user_db, есть service_user
                return service_user

        # Нет oauth_user_db, нет service_user по id
        try:
            service_user = await self.user_service.get_user_by_email(
                user_data.email.lower()
            )
        except ObjectNotFoundError:
            # Создаем service_user
            service_user = await self.user_service.create_user(
                CreateUserSchema(
                    login=user_data.email,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    password=self._generate_random_password(),
                    email=user_data.email,
                )
            )

        # В любом случае создаем oauth_user_db
        await self.create_oauth_user(user_data, service_user.id)

        # Фиксируем вход пользователя через OAuth
        await self.user_service.save_login_history(service_user.id, user_agent)

        return service_user

    async def get_oauth_user_by_service_user_id(
        self, service_user_id: str
    ) -> db_models.OAuthAccount | None:
        async with self.postgres_session() as session:
            user_scalars = await session.scalars(
                select(db_models.OAuthAccount).where(
                    db_models.OAuthAccount.user_id == service_user_id,
                    db_models.OAuthAccount.provider_type == self.provider_name,
                )
            )
            user = user_scalars.first()

            return user if user else None

    async def delete_oauth_account(self, login: str) -> None:
        service_user = await self.user_service.get_user_by_login(login)

        if service_user is None:
            raise ObjectNotFoundError

        oauth_user = await self.get_oauth_user_by_service_user_id(service_user.id)
        if oauth_user is None:
            raise OAuthUserNotFoundError

        async with self.postgres_session() as session:
            await session.delete(oauth_user)
            await session.commit()


@lru_cache()
def get_google_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
    user_service: UserService = Depends(get_user_service),
) -> OAuthServiceGoogle:
    return OAuthServiceGoogle(postgres_session, user_service)
