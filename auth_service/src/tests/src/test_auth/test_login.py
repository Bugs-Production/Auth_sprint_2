import pytest
from fastapi import status

from tests import constants


class TestAuthLogin:
    def setup_method(self):
        self.endpoint = "/api/v1/auth/login"

    @pytest.mark.asyncio
    async def test_login_success(self, async_client, moderator, access_token_moderator):
        login_response = await async_client.post(
            url=self.endpoint,
            json={
                "login": constants.MODERATOR_LOGIN,
                "password": constants.MODERATOR_PASSWORD,
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        response_data = login_response.json()
        for field in ("access_token", "refresh_token"):
            assert field in response_data

        # Проверяем историю логинов пользователя

        login_history_url = f"/api/v1/users/{moderator.id}/login_history"

        login_history_response = await async_client.get(
            login_history_url,
            headers={
                "Authorization": f"Bearer {access_token_moderator}",
            },
        )

        assert login_history_response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "user_data, expected_status, expected_fields",
        [
            (
                # Пользователь есть, но ввел неправильный пароль
                {
                    "login": constants.ADMIN_LOGIN,
                    "password": "wrong_admin_password",
                },
                status.HTTP_400_BAD_REQUEST,
                (),
            ),
            (
                # Пользователя нет в БД
                {
                    "login": "unknown_user",
                    "password": "unknown_pass",
                },
                status.HTTP_404_NOT_FOUND,
                (),
            ),
            (
                # Введены некорректные данные
                {
                    "password": "password",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                # Введены некорректные данные
                {
                    "login": "",
                    "password": "password",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                # Введены некорректные данные
                {
                    "login": "unknown_user",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                # Введены некорректные данные
                {
                    "login": "unknown_user",
                    "password": "",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_login_failed(
        self, async_client, admin, user_data, expected_status, expected_fields
    ):
        response = await async_client.post(url=self.endpoint, json=user_data)

        assert response.status_code == expected_status

        response_data = response.json()
        for field in expected_fields:
            assert field in response_data
