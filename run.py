# start the django server
import webbrowser

from django.core.management import execute_from_command_line

webbrowser.open("http://localhost:8000", new=2)
execute_from_command_line(["manage.py", "runserver", "localhost:8000"])
