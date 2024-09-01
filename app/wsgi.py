"""
WSGI config for PLSOM project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from app.env import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"app.settings.{env}")
application = get_wsgi_application()
