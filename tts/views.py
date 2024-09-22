# ruff: noqa: E402
import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import datetime

from django import forms
from django.conf import settings
from django.http import HttpResponse

# from django.utils.decorators import method_decorator
from django.views.generic import FormView
from melo.api import TTS

from app import utils

# from app.decorators import login_required

# Create your views here.


VOICE_ROOT = settings.VOICE_ROOT

SPEAKERS = {
    "EN": ["EN-Default", "EN-US", "EN-BR", "EN_INDIA", "EN-AU"],
    "FR": ["FR"],
    "JP": ["JP"],
    "ES": ["ES"],
    "ZH": ["ZH"],
    "KR": ["KR"],
}


class TextToSpeechForm(forms.Form):
    text = forms.CharField(
        label="Enter Your Text",
        widget=forms.Textarea(
            attrs={
                "class": "form-control my-3 border",
                "id": "text",
                "placeholder": "Enter your text here...",
            }
        ),
        required=True,
    )
    language = forms.ChoiceField(
        label="Select Language",
        choices=[(lang, lang) for lang in SPEAKERS.keys()],
        widget=forms.Select(
            attrs={"class": "form-control my-3 border", "id": "language"}
        ),
        required=True,
    )
    speaker = forms.ChoiceField(
        label="Select Speaker",
        choices=[(speaker, speaker) for speaker in SPEAKERS["EN"]],
        widget=forms.Select(
            attrs={"class": "form-control my-3 border", "id": "voice"}
        ),
        required=True,
    )
    speed = forms.FloatField(
        label="Speed",
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "id": "diffusion",
                "min": "0.5",
                "max": "2",
                "step": "0.5",
                "value": "1",
                "oninput": "changeInput(event)",
            }
        ),
        required=False,
    )


# @method_decorator([login_required], name="dispatch")
class TextToSpeechView(FormView):
    template_name = "pages/tts.html"
    form_class = TextToSpeechForm

    def form_valid(self, form):
        text = form.cleaned_data["text"]
        language = form.cleaned_data["language"]
        speaker = form.cleaned_data["speaker"]
        speed = form.cleaned_data["speed"]
        id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        model = TTS(language=language)
        voice_tensor = model.hps.data.spk2id[speaker]
        filename = f"{id}.wav"
        upload_path = utils.get_media_path(filename, "synthesized")
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        model.tts_to_file(
            text,
            voice_tensor,
            upload_path,
            speed=speed,
        )
        file_url = utils.get_media_url(filename, "synthesized")
        return HttpResponse(
            f'<audio controls><source src="{file_url}" type="audio/wav"></audio>'
        )

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
