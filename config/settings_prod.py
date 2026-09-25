"""
Production settings. Extends config.settings and is selected with
DJANGO_SETTINGS_MODULE=config.settings_prod (set in .docker/Dockerfile.prod).

Every value that differs per environment must come from the environment; the
deploy workflow renders them from GitHub secrets into the droplet's .env.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from config.settings import *  # noqa: F401,F403
from config.settings import BASE_DIR, SIMPLE_JWT


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"Missing required environment variable {name}")
    return value


def env_list(name: str) -> list[str]:
    return [item for item in os.environ.get(name, "").split(",") if item]


DEBUG = False

SECRET_KEY = env_required("DJANGO_SECRET_KEY")
# The base settings bind the JWT signing key to the insecure dev key at import time
SIMPLE_JWT = {**SIMPLE_JWT, "SIGNING_KEY": SECRET_KEY}

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Missing required environment variable DJANGO_ALLOWED_HOSTS"
    )

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

STATIC_ROOT = BASE_DIR / "staticfiles"

# TLS terminates at nginx, which forwards the original scheme and handles
# the HTTP -> HTTPS redirect and HSTS header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SILENCED_SYSTEM_CHECKS = ["security.W004", "security.W008"]
