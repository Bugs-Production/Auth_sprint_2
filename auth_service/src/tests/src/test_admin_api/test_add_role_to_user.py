from uuid import uuid4

import pytest
from fastapi import status

from tests import constants


class TestAdminAddRolesApi:
    def setup_method(self):
        self.endpoint = "/api/v1/users/"

    @pytest.mark.parametrize(
        "role_id, expected_answer",
        [
            # пытаемся добавить админом существующую роль
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
            # пытаемся добавить админом несуществующую роль
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
    async def test_add_role_with_admin_role(
        self,
        async_client,
        moderator,
        headers_admin,
        role_id,
        role,
        expected_answer,
    ):
        response = await async_client.post(
            url=self.endpoint + moderator.id + "/roles",
            headers=headers_admin,
            json={
                "role_id": role_id,
            },
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]

    @pytest.mark.parametrize(
        "role_id, expected_answer",
        [
            # пытаемся добавить НЕ админом существующую роль
            (
                constants.TEST_ROLE_UUID,
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "answer": constants.FORBIDDEN_RESPONSE,
                },
            )
        ],
    )
    @pytest.mark.asyncio
    async def test_add_role_without_admin_role(
        self,
        async_client,
        moderator,
        headers_moderator,
        role,
        role_id,
        expected_answer,
    ):
        response = await async_client.post(
            url=self.endpoint + moderator.id + "/roles",
            headers=headers_moderator,
            json={
                "role_id": role_id,
            },
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]

    @pytest.mark.parametrize(
        "role_id, expected_answer",
        [
            # пытаемся добавить роль незалогиненным юзером
            (
                constants.TEST_ROLE_UUID,
                {
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "answer": constants.NOT_AUTHENTICATED_RESPONSE,
                },
            )
        ],
    )
    @pytest.mark.asyncio
    async def test_add_role_anonymous_user(
        self, async_client, moderator, role, role_id, expected_answer
    ):
        response = await async_client.post(
            url=self.endpoint + moderator.id + "/roles",
            json={
                "role_id": role_id,
            },
        )
        assert response.status_code == expected_answer["status"]
        assert response.json() == expected_answer["answer"]
