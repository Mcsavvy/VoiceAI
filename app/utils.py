import os

from django.conf import settings


def get_media_path(filename: str, folder: str | None = None) -> str:
    return (
        os.path.join(settings.MEDIA_ROOT, folder, filename)
        if folder
        else os.path.join(settings.MEDIA_ROOT, filename)
    )


def get_voice_path(filename: str, folder: str | None = None) -> str:
    return (
        os.path.join(settings.VOICE_ROOT, folder, filename)
        if folder
        else os.path.join(settings.VOICE_ROOT, filename)
    )
