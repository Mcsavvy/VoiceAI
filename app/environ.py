"""Utility functions for application."""

import inspect
import os
import sys
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import wraps
from logging import getLogger
from typing import (
    Any,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

T = TypeVar("T", bound=Any)
P = ParamSpec("P")
R = TypeVar("R")
MISSING = object()


def _extract_env_vars(text: str) -> dict[str, str]:
    """Extract environment variables from a string."""
    env_vars = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, value = line.split("=", 1)
        env_vars[name.strip()] = value.strip()
    return env_vars


def loadenv(override: bool = False, env_file: str | None = None):
    """Load the environment variables from the env file."""
    if getboolenv("ENV_LOADED", False):
        return
    env_file = env_file or getenv("ENV_FILE", ".env")
    if env_file and os.path.exists(env_file):
        try:
            with open(env_file) as f:
                env_vars = _extract_env_vars(f.read())
        except Exception as e:
            raise RuntimeError(
                f"Failed to load environment variables from {env_file!r}"
            ) from e
        for name, value in env_vars.items():
            if override or name not in os.environ:
                os.environ[name] = value
            else:
                os.environ.setdefault(name, value)
        os.environ["ENV_LOADED"] = "True"
    elif env_file:
        sys.stderr.write(f"Warning: {env_file!r} does not exist.\n")


@overload
def getenv(name: str) -> str: ...


@overload
def getenv(name: str, default: T) -> str | T: ...


def getenv(name: str, default: str | T = MISSING) -> str | T:  # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return os.environ[name]
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default


@overload
def getlistenv(name: str) -> list[str]: ...


@overload
def getlistenv(name: str, default: T) -> list[str] | T: ...


def getlistenv(name: str, default: list[str] | T = MISSING) -> list[str] | T:  # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return os.environ[name].split(",")
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default


@overload
def getintenv(name: str) -> int: ...


@overload
def getintenv(name: str, default: T) -> int | T: ...


def getintenv(name: str, default: int | T = MISSING) -> int | T:  # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return int(os.environ[name])
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default


@overload
def getfloatenv(name: str) -> float: ...


@overload
def getfloatenv(name: str, default: T) -> float | T: ...


def getfloatenv(name: str, default: float | T = MISSING) -> float | T:  # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return float(os.environ[name])
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default


@overload
def getboolenv(name: str) -> bool: ...


@overload
def getboolenv(name: str, default: T) -> bool | T: ...


def getboolenv(name: str, default: bool | T = MISSING) -> bool | T:  # type: ignore[assignment]
    """Get environment variable or return default value."""
    try:
        return os.environ[name].lower() in ["true", "1", "yes"]
    except KeyError:
        if default is MISSING:
            raise RuntimeError(
                f"Environment variable {name!r} is not set."
            ) from None
        return default


@dataclass
class timed:  # noqa: N801
    """Timer context manager."""

    name: str | None = None
    output: str | Callable[[float], str] = "{name} took: {seconds:0.4f} seconds"
    initial_text: bool | str = False
    interrupt_output: str | Callable[[float], str] = (
        "{name} interrupted after {seconds:0.4f} seconds"
    )
    logger: Callable[[str], Any] | None = field(
        default_factory=lambda: getLogger("timer").info
    )

    def start(self):
        """Start the timer."""
        self._start = time.perf_counter()
        if self.logger and self.initial_text:
            if isinstance(self.initial_text, str):
                initial_text = self.initial_text.format(name=self.name)
            elif self.name:
                initial_text = f"{self.name} started"
            else:
                initial_text = "Operation started"
            self.logger(initial_text)

    def interrupt(self):
        """Interrupt the timer."""
        self._end = time.perf_counter()
        self._interval = self._end - self._start
        if self.logger:
            if callable(self.interrupt_output):
                self.logger(self.interrupt_output(self._interval))
            else:
                self.logger(
                    self.interrupt_output.format(
                        name=self.name, seconds=self._interval
                    )
                )

    def stop(self):
        """Stop the timer."""
        self._end = time.perf_counter()
        self._interval = self._end - self._start
        if self.logger:
            if callable(self.output):
                self.logger(self.output(self._interval))
            else:
                self.logger(
                    self.output.format(name=self.name, seconds=self._interval)
                )

    def __enter__(self):
        """Enter the context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        if exc_type:
            self.interrupt()
        else:
            self.stop()
        return False

    async def __aenter__(self):
        """Enter the context manager."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        return self.__exit__(exc_type, exc_value, traceback)

    @overload
    def __call__(self, func: Callable[P, R]) -> Callable[P, R]: ...

    @overload
    def __call__(
        self, func: Callable[P, Awaitable[R]]
    ) -> Callable[P, Awaitable[R]]: ...


    def __call__(  # type: ignore
        self, func: Callable[P, R | Awaitable[R]]
    ) -> Callable[P, R | Awaitable[R]]:
        """Decorator for timing a function."""
        if not self.name:
            self.name = getattr(func, "name", func.__name__)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            self.start()
            try:
                result = func(*args, **kwargs)
                self.stop()
                return result
            except Exception as e:
                self.interrupt()
                raise e

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs):
            self.start()
            try:
                result = await cast(Awaitable[Any], func(*args, **kwargs))
                self.stop()
                return result
            except Exception as e:
                self.interrupt()
                raise e

        if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(
            func
        ):
            return async_wrapper

        return wrapper