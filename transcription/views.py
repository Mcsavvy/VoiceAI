import os
import uuid
from os import path

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse

# from django.utils.decorators import method_decorator
from django.views.generic import FormView
from faster_whisper import WhisperModel
from whisper.tokenizer import LANGUAGES

from app.settings import base as settings

# from app.decorators import login_required

# Create your views here.


class TranscriptionForm(forms.Form):
    audio = forms.FileField()
    language = forms.ChoiceField(
        label="Select Language",
        choices=[(lang, LANGUAGES[lang]) for lang in LANGUAGES],
        widget=forms.Select(
            attrs={"class": "form-control my-3 border", "id": "language"}
        ),
        required=False,
    )

    class Meta:
        fields = ["audio"]
        widgets = {
            "audio": forms.FileInput(attrs={"accept": "audio/*"}),
        }


# @method_decorator([login_required], name="dispatch")
class TranscriptionView(FormView):
    form_class = TranscriptionForm
    template_name = "pages/transcription.html"

    def form_valid(self, form):
        audio: UploadedFile = form.cleaned_data["audio"]
        language = form.cleaned_data.get("language")

        id = uuid.uuid4()
        os.makedirs("tmp", exist_ok=True)
        model = WhisperModel(
            settings.WHISPER_MODEL,
            device="auto",
        )
        temp_audio_path = f"tmp/{id}{path.splitext(audio.name)[1]}"
        with open(temp_audio_path, "wb") as f:
            for chunk in audio.chunks():
                f.write(chunk)
        segments, info = model.transcribe(
            temp_audio_path, beam_size=5, language=language
        )
        print(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )
        texts: list[str] = []
        for segment in segments:
            texts.append(segment.text)
            print(
                "[%.2fs -> %.2fs] %s"
                % (segment.start, segment.end, segment.text)
            )
        return HttpResponse(" ".join(texts))

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
