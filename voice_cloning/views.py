import datetime
import os

import numpy as np
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from scipy.io.wavfile import write

from app import utils
from app.decorators import login_required
from StyleTTS2 import msinference
from StyleTTS2.text_utils import split_and_recombine_text


class VoiceCloneForm(forms.Form):
    text = forms.CharField(
        label="Enter Your Text",
        widget=forms.Textarea(
            attrs={
                "class": "form-control my-3 border",
                "id": "text",
                "rows": "4",
                "placeholder": "Enter your text here",
            }
        ),
        required=True,
    )
    voice = forms.FileField(
        label="Upload Your Audio File",
        required=True,
        widget=forms.FileInput(
            attrs={"class": "d-none", "id": "voice", "accept": "audio/*"}
        ),
    )
    diffusion = forms.IntegerField(
        label="Diffusion",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "id": "diffusion",
                "min": "1",
                "max": "20",
                "step": "1",
                "value": "5",
                "oninput": "changeInput(event)",
            }
        ),
    )

    embedding_scale = forms.IntegerField(
        label="Embedding Scale",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "id": "embedding_scale",
                "min": "1",
                "max": "10",
                "step": "1",
                "value": "1",
                "oninput": "changeInput(event)",
            }
        ),
    )

    alpha = forms.FloatField(
        label="Alpha",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "id": "embedding_scale",
                "min": "0",
                "max": "1",
                "step": "0.1",
                "value": "0.3",
                "oninput": "changeInput(event, 1, true)",
            }
        ),
    )

    beta = forms.FloatField(
        label="Beta",
        required=True,
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "id": "embedding_scale",
                "min": "0",
                "max": "1",
                "step": "0.1",
                "value": "0.7",
                "oninput": "changeInput(event, 1, true)",
            }
        ),
    )


@method_decorator([login_required], name="dispatch")
class VoiceCloneView(FormView):
    template_name = "pages/voice-cloning.html"
    form_class = VoiceCloneForm

    def form_valid(self, form):
        text = form.cleaned_data["text"]
        voice: UploadedFile = form.cleaned_data["voice"]
        diffusion = form.cleaned_data["diffusion"]
        embedding_scale = form.cleaned_data["embedding_scale"]
        alpha = form.cleaned_data["alpha"]
        beta = form.cleaned_data["beta"]

        texts = split_and_recombine_text(text)
        id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{id}.wav"
        if voice.name:
            filename = f"{os.path.splitext(voice.name)[0]}-{id}.wav"
        voice_path = utils.get_voice_path(filename, "uploads")
        os.makedirs(os.path.dirname(voice_path), exist_ok=True)
        with open(voice_path, "wb") as f:
            for chunk in voice.chunks():
                f.write(chunk)
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
        upload_path = utils.get_media_path(filename, "clones")
        file_url = utils.get_media_url(filename, "clones")
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        write(upload_path, 24000, np.concatenate(audios))
        return HttpResponse(
            f'<audio controls><source src="{file_url}" type="audio/wav"></audio>'
        )

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
