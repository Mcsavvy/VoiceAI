from django.urls import path

from . import views

urlpatterns = [
    path("", views.TranscriptionView.as_view(), name="transcription"),
]
