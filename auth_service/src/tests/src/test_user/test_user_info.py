import uuid

import pytest
from fastapi import status

from tests import constants


class TestUserInfo:
    def setup_method(self):
        self.endpoint = "/api/v1/users"

    @pytest.mark.parametrize(
        "user_id, expected_status, expected_fields",
        [
            # проверка информации о модераторе
            (
                constants.MODERATOR_UUID,
                status.HTTP_200_OK,
                ("login", "first_name", "last_name", "email", "birthdate"),
            ),
            # проверка несуществующего пользователя
            (
                str(uuid.uuid4()),
                status.HTTP_404_NOT_FOUND,
                ("detail",),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_with_admin_role(
        self,
        async_client,
        headers_admin,
        moderator,
        user_id,
        expected_status,
        expected_fields,
    ):
        response = await async_client.get(
            url=f"{self.endpoint}/{user_id}",
            headers=headers_admin,
        )
        assert response.status_code == expected_status
        response_data = response.json()
        for field in expected_fields:
            assert field in response_data

    @pytest.mark.asyncio
    async def test_with_invalid_token(
        self,
        async_client,
        moderator,
        headers_admin_invalid,
    ):

        response = await async_client.get(
            url=f"{self.endpoint}/{moderator.id}",
            headers=headers_admin_invalid,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_without_admin_role(
        self,
        async_client,
        admin,
        headers_moderator,
    ):
        response = await async_client.get(
            url=f"{self.endpoint}/{admin.id}",
            headers=headers_moderator,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_by_anonymous(self, async_client, admin):
        response = await async_client.get(
            url=f"{self.endpoint}/{admin.id}",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
