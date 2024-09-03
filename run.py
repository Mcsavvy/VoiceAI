# start the django server
import os
import webbrowser

from django.core.management import execute_from_command_line

from app.env import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"app.settings.{env}")

webbrowser.open("http://localhost:8000", new=2)
execute_from_command_line(["manage.py", "runserver", "localhost:8000"])
