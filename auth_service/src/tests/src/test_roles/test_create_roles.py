import pytest
from fastapi import status


class TestApiPostRoles:
    """Тестируем поведение endpoint POST /api/v1/roles/"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    # Фикстура для данных новой роли
    @pytest.fixture
    def role_data(self):
        return {"title": "new role"}

    @pytest.mark.asyncio
    async def test_successfully_create_role(
        self, async_client, role_data, headers_admin
    ):
        response_post = await async_client.post(
            self.endpoint, headers=headers_admin, json=role_data
        )
        assert (
            response_post.status_code == status.HTTP_200_OK
        ), "Role creation should succeed"
        assert response_post.json() == role_data, "Response data mismatch"

        # Убедимся, что роль действительно появилась в базе
        response_get = await async_client.get(self.endpoint, headers=headers_admin)

        assert (
            response_get.status_code == status.HTTP_200_OK
        ), "Fetching roles should succeed"
        roles_in_db = [role["title"] for role in response_get.json().get("items")]

        assert "new role" in roles_in_db, "Newly created role not found in the database"
        assert (
            len(roles_in_db) == 2
        ), "There should be exactly two roles in the database"

    @pytest.mark.asyncio
    async def test_not_successfully_create_role_bad_request(
        self, async_client, headers_admin
    ):
        invalid_data = {"title": 1}  # Некорректные данные
        response = await async_client.post(
            self.endpoint, headers=headers_admin, json=invalid_data
        )
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        ), "Invalid data should return 422"
        assert (
            response.json().get("detail")[0].get("msg")
            == "Input should be a valid string"
        ), "Validation error message mismatch"

    @pytest.mark.asyncio
    async def test_create_role_anonymous_user(self, async_client, role_data):
        response = await async_client.post(self.endpoint, json=role_data)
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "Anonymous user should not be authorized"
        assert (
            response.json().get("detail") == "Not authenticated"
        ), "Detail message mismatch"

    @pytest.mark.asyncio
    async def test_create_role_moderator_user(
        self, async_client, headers_moderator, role_data
    ):
        response = await async_client.post(
            self.endpoint, headers=headers_moderator, json=role_data
        )

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Moderator should not have permission to create roles"
        assert response.json().get("detail") == "Forbidden", "Detail message mismatch"

    @pytest.mark.asyncio
    async def test_create_role_duplication(
        self, async_client, headers_admin, role_data
    ):
        # Первое создание роли
        response = await async_client.post(
            self.endpoint, headers=headers_admin, json=role_data
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), "First role creation should succeed"
        assert (
            response.json() == role_data
        ), "Response data mismatch after first creation"

        # Попытка создать такую же роль
        response_duplication = await async_client.post(
            self.endpoint, headers=headers_admin, json=role_data
        )

        assert (
            response_duplication.status_code == status.HTTP_400_BAD_REQUEST
        ), "Duplicate role should return 400"
        assert (
            response_duplication.json().get("detail")
            == "Role with title new role already exists"
        ), "Duplication error message mismatch"
