import uuid

import pytest
from fastapi import status


class TestApiPutRoles:
    """Тестируем поведение endpoint PUT /api/v1/roles/{role_id}"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    # Фикстура для создания данных запроса
    @pytest.fixture
    def request_data(self, role):
        return {"id": str(role.id), "title": "new role 2"}

    @pytest.mark.asyncio
    async def test_successfully_change_role(
        self, async_client, headers_admin, request_data, role
    ):
        response = await async_client.put(
            f"{self.endpoint}{role.id}", headers=headers_admin, json=request_data
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Role should be successfully updated"
        assert (
            response.json().get("title") == request_data["title"]
        ), "Title should be updated"

    @pytest.mark.asyncio
    async def test_not_found_change_role(
        self, async_client, headers_admin, request_data
    ):
        random_id = uuid.uuid4()
        response = await async_client.put(
            f"{self.endpoint}{random_id}", headers=headers_admin, json=request_data
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), "Non-existent role should return 404"
        assert response.json().get("detail") == "Role not found."

    @pytest.mark.asyncio
    async def test_moderator_change_role(
        self, async_client, headers_moderator, request_data, role
    ):
        response = await async_client.put(
            f"{self.endpoint}{role.id}", headers=headers_moderator, json=request_data
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Moderator should not have permission to change roles"
        assert response.json().get("detail") == "Forbidden"

    @pytest.mark.asyncio
    async def test_anonymous_user_change_role(self, async_client, request_data, role):
        response = await async_client.put(
            f"{self.endpoint}{role.id}", json=request_data
        )

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "Anonymous user should not be authorized"
        assert response.json().get("detail") == "Not authenticated"
