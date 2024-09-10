import pytest
from fastapi import status


class TestAuthSignup:
    def setup_method(self):
        self.endpoint = "/api/v1/auth/signup"

    @pytest.mark.parametrize(
        "user_data, expected_status, expected_fields",
        [
            (
                {
                    "login": "user1",
                    "password": "pass1",
                    "first_name": "user1_first_name",
                    "last_name": "user1_last_name",
                },
                status.HTTP_200_OK,
                ("access_token", "refresh_token"),
            ),
            (
                {
                    "password": "pass1",
                    "first_name": "user1_first_name",
                    "last_name": "user1_last_name",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                {
                    "login": "user1",
                    "first_name": "user1_first_name",
                    "last_name": "user1_last_name",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                {
                    "login": "",
                    "password": "pass1",
                    "first_name": "user1_first_name",
                    "last_name": "user1_last_name",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                {
                    "login": "user1",
                    "password": "",
                    "first_name": "user1_first_name",
                    "last_name": "user1_last_name",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                (),
            ),
            (
                {
                    "login": "user1",
                    "password": "pass1",
                    "first_name": "",
                    "last_name": "",
                },
                status.HTTP_200_OK,
                ("access_token", "refresh_token"),
            ),
            (
                {
                    "login": "user1",
                    "password": "pass1",
                },
                status.HTTP_200_OK,
                ("access_token", "refresh_token"),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_signup(
        self, async_client, user_data, expected_status, expected_fields
    ):
        response = await async_client.post(url=self.endpoint, json=user_data)

        assert response.status_code == expected_status

        response_data = response.json()
        for field in expected_fields:
            assert field in response_data
