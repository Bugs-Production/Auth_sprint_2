import uuid

import pytest
from fastapi import status

from models.roles import Role


class TestApiGetRoles:
    """Тестируем поведение endpoint GET /api/v1/roles/"""

    def setup_method(self):
        self.endpoint = "/api/v1/roles/"

    @pytest.mark.asyncio
    async def test_admin_can_successfully_get_roles(self, async_client, headers_admin):
        response = await async_client.get(self.endpoint, headers=headers_admin)
        assert response.status_code == status.HTTP_200_OK, "Admin should have access"
        assert response.json().get("items") == [
            {"id": "2e796639-9b3f-49c3-9c59-9c3302ae5e59", "title": "admin"}
        ], "Role data mismatch"

    @pytest.mark.asyncio
    async def test_anonymous_user_request(self, async_client):
        response = await async_client.get(self.endpoint)
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "Anonymous users should not have access"
        assert response.json() == {
            "detail": "Not authenticated"
        }, "Error message mismatch for unauthenticated request"

    @pytest.mark.asyncio
    async def test_forbidden_access_with_non_admin_role(
        self, async_client, headers_moderator
    ):
        response = await async_client.get(self.endpoint, headers=headers_moderator)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Non-admin should not have access"
        assert response.json() == {
            "detail": "Forbidden"
        }, "Error message mismatch for unauthorized access"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "page, size, expected_length, expected_page, expected_total, expected_pages",
        [
            (1, 5, 5, 1, 11, 3),  # Первая страница, 5 элементов
            (2, 5, 5, 2, 11, 3),  # Вторая страница, 5 элементов
            (3, 5, 1, 3, 11, 3),  # Третья страница, 1 элемент
            (1, 10, 10, 1, 11, 2),  # Первая страница, 10 элементов
            (2, 10, 1, 2, 11, 2),  # Вторая страница, 1 элемент
            (1, 11, 11, 1, 11, 1),  # Одна страница, 11 элементов
        ],
    )
    async def test_get_roles_paginate(
        self,
        async_client,
        headers_admin,
        create_multiple_roles,
        page,
        size,
        expected_length,
        expected_page,
        expected_total,
        expected_pages,
    ):
        # Запрос с параметрами пагинации
        params = {"page": page, "size": size}
        response = await async_client.get(
            self.endpoint, headers=headers_admin, params=params
        )

        assert response.status_code == status.HTTP_200_OK, "Admin should have access"

        json_response = response.json()
        assert (
            len(json_response["items"]) == expected_length
        ), f"Should return {expected_length} roles"
        assert (
            json_response["total"] == expected_total
        ), f"Total number of roles should be {expected_total}"
        assert (
            json_response["page"] == expected_page
        ), f"Current page should be {expected_page}"
        assert json_response["size"] == size, f"Page size should be {size}"
        assert (
            json_response["pages"] == expected_pages
        ), f"Total number of pages should be {expected_pages}"
