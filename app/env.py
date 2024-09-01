from typing import Literal

from app.environ import getenv

_env = getenv("DJANGO_ENV", "develop")

env: Literal["production", "test", "dev"]

if "prod" in _env:
    env = "production"
elif "test" in _env:
    env = "test"
else:
    env = "dev"
