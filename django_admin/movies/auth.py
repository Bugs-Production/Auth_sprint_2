import http
from logging import getLogger
from time import sleep

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from config.components.auth import (ADMIN_ROLE_KEY, AUTH_SERVICE_HOST,
                                    AUTH_SERVICE_PORT)

User = get_user_model()

logger = getLogger("django")

SLEEP_TIME = 0.5


class AuthServiceBackend(BaseBackend):
    def _check_admin_role(self, user_id, access_token):
        url = (
            f"{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}/auth/api/v1/users/{user_id}/roles"
        )
        page = 1
        page_size = 50

        session = requests.Session()

        while True:
            try:
                response = session.get(
                    url,
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"page": page, "size": page_size},
                )
                if response.status_code != http.HTTPStatus.OK:
                    return False

                items = response.json().get("items", [])

                if not items:
                    break

                for item in items:
                    if item["title"] == ADMIN_ROLE_KEY:
                        return True

                page += 1
                sleep(SLEEP_TIME)

            except Exception as e:
                logger.error(e)
                break
        return False

    def authenticate(self, request, username=None, password=None):
        url = AUTH_SERVICE_HOST + ":" + AUTH_SERVICE_PORT + "/auth/api/v1/auth/login"
        payload = {"login": username, "password": password}
        response = requests.post(url, json=payload)

        if response.status_code != http.HTTPStatus.OK:
            return None

        is_admin = self._check_admin_role(
            user_id=response.json().get("user_id"),
            access_token=response.json().get("access_token"),
        )

        if not is_admin:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
