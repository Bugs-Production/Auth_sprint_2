import os

AUTH_SERVICE_HOST = os.getenv("AUTH_SERVICE_HOST", "127.0.0.1")
AUTH_SERVICE_PORT = os.getenv("AUTH_SERVICE_PORT", "80")

AUTHENTICATION_BACKENDS = [
    "movies.auth.AuthServiceBackend",
]

ADMIN_ROLE_KEY = "admin"
