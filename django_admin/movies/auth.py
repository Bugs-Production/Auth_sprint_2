import http

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from config.components.auth import AUTH_SERVICE_LOGIN_URL

User = get_user_model()

class AuthServiceBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = AUTH_SERVICE_LOGIN_URL
        payload = {"login": username, "password": password}
        response = requests.post(url, json=payload)
        if response.status_code != http.HTTPStatus.OK:
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
