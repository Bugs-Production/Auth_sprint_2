import uuid

import pytest
from fastapi import status

from tests import constants


class TestUserLoginHistory:
    def setup_method(self):
        self.endpoint = "/api/v1/users"

    @pytest.mark.parametrize(
        "pagination_data, expected_length, expected_fields, expected_status",
        [
            (
                {"page": 1, "size": 10},
                5,
                ("event_date", "success"),
                status.HTTP_200_OK,
            ),
            (
                {"page": 1, "size": 3},
                3,
                ("event_date", "success"),
                status.HTTP_200_OK,
            ),
            (
                {"page": 10, "size": 1},
                0,
                (),
                status.HTTP_200_OK,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_with_admin_role(
        self,
        async_client,
        moderator,
        headers_admin,
        login_multiple_times,
        pagination_data,
        expected_length,
        expected_fields,
        expected_status,
    ):
        response = await async_client.get(
            url=f"{self.endpoint}/{moderator.id}/login_history",
            headers=headers_admin,
            params=pagination_data,
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "items" in response_data
        assert len(response_data.get("items")) == expected_length

        for field in expected_fields:
            assert field in response_data.get("items")[0]

    @pytest.mark.asyncio
    async def test_not_exists_user(self, async_client, headers_admin):
        response = await async_client.get(
            url=f"{self.endpoint}/{uuid.uuid4()}/login_history",
            headers=headers_admin,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_with_invalid_token(
        self, async_client, admin, moderator, headers_admin_invalid
    ):
        response = await async_client.get(
            url=f"{self.endpoint}/{moderator.id}/login_history",
            headers=headers_admin_invalid,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "user_id, expected_status",
        [
            # пытаемся посмотреть пользователем свою историю
            (
                constants.MODERATOR_UUID,
                status.HTTP_200_OK,
            ),
            # пытаемся посмотреть пользователем чужую историю
            (
                constants.ADMIN_UUID,
                status.HTTP_403_FORBIDDEN,
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
        expected_status,
    ):
        response = await async_client.get(
            url=f"{self.endpoint}/{user_id}/login_history",
            headers=headers_moderator,
        )

        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_by_anonymous(self, async_client, admin):
        response = await async_client.get(
            url=f"{self.endpoint}/{admin.id}/login_history",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
