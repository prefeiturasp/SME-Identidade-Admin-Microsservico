"""Configuração Django do SME-Identidade-Admin-Microsservico."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "dev-inseguro-apenas-desenvolvimento",
)
API_KEY = os.getenv("API_KEY", "dev-key-default")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
]
NIVEL_LOG = os.getenv("NIVEL_LOG", "INFO")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.autenticacao",
    "apps.keycloak_admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.autenticacao.api.api_key.AutenticacaoApiKey",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-Identidade-Admin-Microsservico API",
    "DESCRIPTION": "API de controle do identidade-Admin",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
}

# Keycloak Admin API
# ambiente já usadas no SME-Identidade-ETL, para manter um único
# padrão de configuração de Keycloak na plataforma.
KEYCLOAK_URL_SERVIDOR = os.getenv(
    "KEYCLOAK_URL_SERVIDOR", "https://localhost:8080/"
)
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "COTIC")
KEYCLOAK_USUARIO_ADMIN = os.getenv("KEYCLOAK_USUARIO_ADMIN", "admin")
KEYCLOAK_SENHA_ADMIN = os.getenv("KEYCLOAK_SENHA_ADMIN", "admin")
KEYCLOAK_VERIFICAR_SSL = (
    os.getenv("KEYCLOAK_VERIFICAR_SSL", "true").lower() == "true"
)
KEYCLOAK_LOGIN_CLIENT_ID = os.getenv(
    "KEYCLOAK_LOGIN_CLIENT_ID", "auto-servico-qa"
)
KEYCLOAK_LOGIN_CLIENT_SECRET = os.getenv("KEYCLOAK_LOGIN_CLIENT_SECRET", "")

# ---------------------------------------------------------------------------
# Logging (python-json-logger — padrão Ateliê)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "nivel",
                "name": "logger",
            },
            "json_ensure_ascii": False,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "identidade_admin": {
            "handlers": ["console"],
            "level": NIVEL_LOG,
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": NIVEL_LOG,
    },
}
