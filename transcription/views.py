import os
import uuid
from os import path

import whisper
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
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


@require_http_methods(["POST"])
def transcribe(request) -> HttpResponse:
    id = uuid.uuid4()
    form = TranscriptionForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
    # transcribe audio
    audio: UploadedFile = form.cleaned_data["audio"]
    os.makedirs("tmp", exist_ok=True)
    temp_audio_path = f"tmp/{id}{path.splitext(audio.name)[1]}"
    with open(temp_audio_path, "wb") as f:
        for chunk in audio.chunks():
            f.write(chunk)
    result = model.transcribe(temp_audio_path, fp16=False)
    return HttpResponse(result["text"])
