import os
import uuid
from os import path

import whisper
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from app.decorators import login_required

model = whisper.load_model("base")

# Create your views here.


class TranscriptionForm(forms.Form):
    audio = forms.FileField()

    class Meta:
        fields = ["audio"]
        widgets = {
            "audio": forms.FileInput(attrs={"accept": "audio/*"}),
        }


@method_decorator([login_required], name="dispatch")
class TranscriptionView(FormView):
    form_class = TranscriptionForm
    template_name = "pages/transcription.html"

    def form_valid(self, form):
        audio: UploadedFile = form.cleaned_data["audio"]
        id = uuid.uuid4()
        os.makedirs("tmp", exist_ok=True)
        temp_audio_path = f"tmp/{id}{path.splitext(audio.name)[1]}"
        with open(temp_audio_path, "wb") as f:
            for chunk in audio.chunks():
                f.write(chunk)
        result = model.transcribe(temp_audio_path, fp16=False)
        return HttpResponse(result["text"])

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
