import os

AUTH_SERVICE_HOST = os.getenv("AUTH_SERVICE_HOST", "127.0.0.1")
AUTH_SERVICE_PORT = os.getenv("AUTH_SERVICE_PORT", "80")
AUTH_SERVICE_LOGIN_URL = (
    AUTH_SERVICE_HOST + ":" + AUTH_SERVICE_PORT + "/auth/api/v1/auth/login"
)

AUTHENTICATION_BACKENDS = [
    "movies.auth.AuthServiceBackend",
]
