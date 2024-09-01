"""Gunicorn configuration file."""

from app.environ import getboolenv, getenv, getintenv

# Server Socket
wsgi_app = "app.wsgi:application"
reload = getboolenv("GUNICORN_RELOAD", False)
HOST = getenv("HOST", "0.0.0.0")
PORT = getintenv("PORT", 8000)
bind = getenv("GUNICORN_BIND", f"{HOST}:{PORT}")
workers = getintenv("GUNICORN_WORKERS", 1)
threads = getintenv("GUNICORN_THREADS", 1)

# Logging
loglevel = getenv("GUNICORN_LOG_LEVEL", getenv("LOG_LEVEL", "info"))
