# ruff: noqa: F405, F403

from app.environ import getenv, getlistenv

from .base import *


def split_connection_string(conn_str: str) -> dict[str, str]:
    """split database connection string into dictionary"""
    conn_str = conn_str.split("://")[1]
    cred, host = conn_str.split("@")
    user, password = cred.split(":")
    host, db = host.split("/")
    host, port = host.split(":")
    return {
        "NAME": db,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
    }


DEBUG = False
ALLOWED_HOSTS = getlistenv("ALLOWED_HOSTS")
SECRET_KEY = getenv("DJANGO_SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        **split_connection_string(getenv("DATABASE_URL")),
    }
}
