import pytest
from fastapi import status

from tests import constants


class TestAdminGetRolesApi:
    def setup_method(self):
        self.endpoint = "/api/v1/users/"

    @pytest.mark.parametrize(
        "user_id, pagination_data, expected_answer",
        [
            # пытаемся посмотреть админом роли пользователя
            (
                constants.MODERATOR_UUID,
                {"page": 1, "size": 10},
                {"status": status.HTTP_200_OK, "items": 2},
            ),
            # тест пустой страницы
            (
                constants.MODERATOR_UUID,
                {"page": 2, "size": 10},
                {"status": status.HTTP_200_OK, "items": 0},
            ),
            # тест следующей страницы с данными
            (
                constants.MODERATOR_UUID,
                {"page": 2, "size": 1},
                {"status": status.HTTP_200_OK, "items": 1},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_role_with_admin_role(
        self,
        async_client,
        moderator,
        add_test_role_to_moderator,
        headers_admin,
        user_id,
        role,
        expected_answer,
        pagination_data,
    ):
        response = await async_client.get(
            url=self.endpoint + moderator.id + "/roles",
            headers=headers_admin,
            params=pagination_data,
        )
        assert response.status_code == expected_answer["status"]
        assert len(response.json()["items"]) == expected_answer["items"]

    @pytest.mark.parametrize(
        "user_id, pagination_data, expected_answer",
        [
            # пытаемся посмотреть пользователем свои роли
            (
                constants.MODERATOR_UUID,
                {"page": 1, "size": 10},
                {"status": status.HTTP_200_OK, "items": 2},
            ),
            # пытаемся посмотреть пользователем чужие роли
            (
                constants.ADMIN_UUID,
                {"page": 1, "size": 10},
                {"status": status.HTTP_403_FORBIDDEN, "items": 0},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_role_without_admin_role(
        self,
        async_client,
        moderator,
        add_test_role_to_moderator,
        headers_moderator,
        user_id,
        role,
        expected_answer,
        pagination_data,
    ):
        response = await async_client.get(
            url=self.endpoint + user_id + "/roles",
            headers=headers_moderator,
            params=pagination_data,
        )
        assert response.status_code == expected_answer["status"]
        assert len(response.json().get("items", [])) == expected_answer["items"]

    @pytest.mark.parametrize(
        "user_id, pagination_data, expected_answer",
        [
            #  пытаемся проверить роли незалогиненным юзером
            (
                constants.MODERATOR_UUID,
                {"page": 1, "size": 10},
                {
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "answer": constants.NOT_AUTHENTICATED_RESPONSE,
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_role_anonymous_user(
        self,
        async_client,
        moderator,
        add_test_role_to_moderator,
        user_id,
        role,
        expected_answer,
        pagination_data,
    ):
        response = await async_client.get(
            url=self.endpoint + user_id + "/roles",
            params=pagination_data,
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]
