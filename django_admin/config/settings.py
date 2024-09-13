import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    "components/application_definition.py",
    "components/database.py",
    "components/internationalization.py",
    "components/auth.py",
)


BASE_DIR = Path(__file__).resolve().parent.parent


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(message)s "
            "[in %(pathname)s:%(lineno)d]",
        },
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "debug-console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["require_debug_true"],
        },
        "console": {
            "level": "INFO",
            "formatter": "verbose",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["debug-console"],
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", False) == "True"

ALLOWED_HOSTS_RAW = os.environ.get("ALLOWED_HOSTS")
ALLOWED_HOSTS = ALLOWED_HOSTS_RAW.split(",") if ALLOWED_HOSTS_RAW else []

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


STATIC_URL = "static/"
STATIC_ROOT = "/app/static"

MEDIA_URL = "media/"
MEDIA_ROOT = "/app/media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
