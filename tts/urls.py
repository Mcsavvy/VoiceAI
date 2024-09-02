from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("convert_text", views.convert_text, name="convert_text"),
    path("voice_clone", views.voice_clone, name="voice_clone"),
    path("handle_voice", views.handle_voice, name="handle_voice"),
]