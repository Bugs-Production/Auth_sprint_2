import uuid

import pytest
from fastapi import status


class TestApiDeleteRoles:
    """Тестируем поведение endpoint DELETE /api/v1/roles/{role_id}"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    @pytest.mark.asyncio
    async def test_successfully_delete_role(self, async_client, headers_admin, role):
        response = await async_client.delete(
            f"{self.endpoint}{role.id}",
            headers=headers_admin,
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Role should be successfully deleted"
        assert (
            response.json().get("detail") == "Role deleted successfully"
        ), "Detail message mismatch"

    @pytest.mark.asyncio
    async def test_not_found_delete_role(self, async_client, headers_admin):
        random_id = uuid.uuid4()
        response = await async_client.delete(
            f"{self.endpoint}{random_id}",
            headers=headers_admin,
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), "Non-existent role should return 404"
        assert (
            response.json().get("detail") == "Role not found."
        ), "Detail message mismatch"

    @pytest.mark.asyncio
    async def test_moderator_user_delete_role(
        self, async_client, headers_moderator, role
    ):
        response = await async_client.delete(
            f"{self.endpoint}{role.id}",
            headers=headers_moderator,
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Moderator should not have permission to delete roles"
        assert response.json().get("detail") == "Forbidden", "Detail message mismatch"

    @pytest.mark.asyncio
    async def test_anonymous_user_delete_role(self, async_client, role):
        response = await async_client.delete(
            f"{self.endpoint}{role.id}",
        )

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "Anonymous user should not be authorized"
        assert (
            response.json().get("detail") == "Not authenticated"
        ), "Detail message mismatch"
