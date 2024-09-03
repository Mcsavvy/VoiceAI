import datetime
import os

import numpy as np
from django import forms
from django.conf import settings
from django.http import HttpResponse

# from django.utils.decorators import method_decorator
from django.views.generic import FormView
from scipy.io.wavfile import write

from app import utils

# from app.decorators import login_required
from StyleTTS2 import msinference
from StyleTTS2.text_utils import split_and_recombine_text

# Create your views here.


def is_voice_file(file):
    return os.path.isfile(file) and os.path.splitext(file)[1] in [
        ".mp3",
        ".wav",
    ]


VOICE_ROOT = settings.VOICE_ROOT
voices = os.listdir(VOICE_ROOT)
voices = filter(
    lambda x: is_voice_file(os.path.join(VOICE_ROOT, x)),
    voices,
)


class TextToSpeechForm(forms.Form):
    text = forms.CharField(
        label="Enter Your Text",
        max_length=1000,
        widget=forms.Textarea(
            attrs={"class": "form-control my-3 border", "id": "text"}
        ),
        required=True,
    )
    voice = forms.ChoiceField(
        label="Select Voice",
        choices=[(voice, voice) for voice in voices],
        widget=forms.Select(
            attrs={"class": "form-control my-3 border", "id": "voice"}
        ),
        required=True,
    )


# @method_decorator([login_required], name="dispatch")
class TextToSpeechView(FormView):
    template_name = "pages/tts.html"
    form_class = TextToSpeechForm

    def form_valid(self, form):
        text = form.cleaned_data["text"]
        voice = form.cleaned_data["voice"]
        diffusion = 5
        embedding_scale = 1
        alpha = 0.3
        beta = 0.7
        texts = split_and_recombine_text(text)
        id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{id}.wav"
        voice_path = utils.get_voice_path(voice)
        voice_tensor = msinference.compute_style(voice_path)
        audios = []
        for text in texts:
            audios.append(
                msinference.inference(
                    text,
                    voice_tensor,
                    alpha=alpha,
                    beta=beta,
                    diffusion_steps=diffusion,
                    embedding_scale=embedding_scale,
                )
            )
        upload_path = utils.get_media_path(filename, "synthesized")
        file_url = utils.get_media_url(filename, "synthesized")
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        write(upload_path, 24000, np.concatenate(audios))
        return HttpResponse(
            f'<audio controls><source src="{file_url}" type="audio/wav"></audio>'
        )

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
