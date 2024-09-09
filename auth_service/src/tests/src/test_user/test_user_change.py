from datetime import datetime

import pytest
from fastapi import status

from tests import constants


class TestUserChange:
    def setup_method(self):
        self.endpoint = "/api/v1/users"

    @pytest.mark.parametrize(
        "user_id, change_data, expected_status, expected_fields",
        [
            # валидный запрос
            (
                constants.MODERATOR_UUID,
                {
                    "login": "new_username",
                    "password": "new_pass1",
                    "first_name": "new_first_name",
                    "last_name": "new_last_name",
                    "email": "new_email@example.com",
                    "birthdate": datetime.today().strftime("%Y-%m-%d"),
                },
                status.HTTP_200_OK,
                ("login", "password", "first_name", "last_name", "email", "birthdate"),
            ),
            # использовать login существующего пользователя
            (
                constants.MODERATOR_UUID,
                {
                    "login": constants.ADMIN_LOGIN,
                },
                status.HTTP_409_CONFLICT,
                ("detail",),
            ),
            # попытка изменить данные другого пользователя
            (
                constants.ADMIN_UUID,
                {
                    "login": "new_username",
                },
                status.HTTP_403_FORBIDDEN,
                ("detail",),
            ),
            # отсутствуют данные для замены [check_at_least_one_field_exists]
            (
                constants.MODERATOR_UUID,
                {},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                ("detail",),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_without_admin_role(
        self,
        async_client,
        admin,
        moderator,
        headers_moderator,
        user_id,
        change_data,
        expected_status,
        expected_fields,
    ):
        response = await async_client.put(
            url=f"{self.endpoint}/{user_id}",
            json=change_data,
            headers=headers_moderator,
        )

        assert response.status_code == expected_status

        for field in expected_fields:
            assert field in response.json()

    @pytest.mark.parametrize(
        "user_id, change_data, expected_status, expected_fields",
        [
            # валидный запрос
            (
                constants.MODERATOR_UUID,
                {
                    "login": "new_username",
                    "password": "new_pass1",
                    "first_name": "new_first_name",
                    "last_name": "new_last_name",
                    "email": "new_email@example.com",
                    "birthdate": datetime.today().strftime("%Y-%m-%d"),
                },
                status.HTTP_200_OK,
                ("login", "password", "first_name", "last_name", "email", "birthdate"),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_with_admin_role(
        self,
        async_client,
        admin,
        headers_admin,
        moderator,
        user_id,
        change_data,
        expected_status,
        expected_fields,
    ):
        response = await async_client.put(
            url=f"{self.endpoint}/{user_id}", json=change_data, headers=headers_admin
        )

        assert response.status_code == expected_status

        for field in expected_fields:
            assert field in response.json()

    @pytest.mark.asyncio
    async def test_by_anonymous(self, async_client, admin):
        response = await async_client.put(f"{self.endpoint}/{admin.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
