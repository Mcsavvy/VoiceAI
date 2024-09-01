# ruff: noqa: F405, F403

from os import getenv

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["django_browser_reload"]
INSTALLED_APPS.insert(
    INSTALLED_APPS.index("django.contrib.staticfiles") + 1,
    "whitenoise.runserver_nostatic",
)
MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

try:
    from .local import *  # type: ignore
except ImportError:
    pass
