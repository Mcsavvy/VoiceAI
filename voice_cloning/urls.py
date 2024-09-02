from django.urls import path

from . import views

urlpatterns = [
    path("", views.VoiceCloneView.as_view(), name="voice_cloning"),
]
