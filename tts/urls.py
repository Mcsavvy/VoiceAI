from django.urls import path

from . import views

urlpatterns = [
    path("", views.TextToSpeechView.as_view(), name="tts"),
]
