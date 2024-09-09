from uuid import uuid4

import pytest
from fastapi import status

from tests import constants


class TestAdminRemoveRolesApi:
    def setup_method(self):
        self.endpoint = "/api/v1/users/"

    @pytest.mark.parametrize(
        "role_id, expected_answer",
        [
            # пытаемся удалить админом существующую роль
            (
                constants.TEST_ROLE_UUID,
                {
                    "status": status.HTTP_200_OK,
                    "answer": {
                        "id": constants.TEST_ROLE_UUID,
                        "title": "new role",
                    },
                },
            ),
            # пытаемся удалить админом несуществующую роль
            (
                str(uuid4()),
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "answer": constants.ROLE_NOT_FOUND_RESPONSE,
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_delete_role_with_admin_role(
        self,
        async_client,
        moderator,
        add_test_role_to_moderator,
        headers_admin,
        role_id,
        role,
        expected_answer,
    ):
        response = await async_client.delete(
            url=self.endpoint + moderator.id + "/roles/" + role_id,
            headers=headers_admin,
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]

    @pytest.mark.parametrize(
        "role_id, expected_answer",
        [
            # пытаемся удалить НЕ админом существующую роль
            (
                constants.TEST_ROLE_UUID,
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "answer": constants.FORBIDDEN_RESPONSE,
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_delete_role_without_admin_role(
        self,
        async_client,
        moderator,
        add_test_role_to_moderator,
        headers_moderator,
        role_id,
        role,
        expected_answer,
    ):
        response = await async_client.delete(
            url=self.endpoint + moderator.id + "/roles/" + role_id,
            headers=headers_moderator,
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]

    @pytest.mark.parametrize(
        "role_id, expected_answer",
        [
            # пытаемся удалить роль незалогиненным юзером
            (
                constants.TEST_ROLE_UUID,
                {
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "answer": constants.NOT_AUTHENTICATED_RESPONSE,
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_delete_role_anonymous_user(
        self,
        async_client,
        moderator,
        add_test_role_to_moderator,
        role_id,
        role,
        expected_answer,
    ):
        response = await async_client.delete(
            url=self.endpoint + moderator.id + "/roles/" + role_id
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]
