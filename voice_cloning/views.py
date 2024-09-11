# ruff: noqa: E402
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import datetime
import os

import torch
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse

# from django.utils.decorators import method_decorator
from django.views.generic import FormView
from faster_whisper import WhisperModel
from melo.api import TTS
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

from app import utils

VOICE_ROOT = settings.VOICE_ROOT

se_extractor.model = WhisperModel(
    settings.WHISPER_MODEL,
    device="auto",
)

SPEAKERS = {
    "EN": ["EN-Default", "EN-US", "EN-BR", "EN_INDIA", "EN-AU"],
    "FR": ["FR"],
    "JP": ["JP"],
    "ES": ["ES"],
    "ZH": ["ZH"],
    "KR": ["KR"],
}

CHECKPONT_PATH: str = settings.OPENVOICE_V2_CHECKPOINT_PATH
ckpt_converter = os.path.join(CHECKPONT_PATH, "converter")
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# from app.decorators import login_required


class VoiceCloneForm(forms.Form):
    voice = forms.FileField(
        label="Upload Your Audio File",
        required=True,
        widget=forms.FileInput(
            attrs={"class": "d-none", "id": "voice", "accept": "audio/*"}
        ),
    )
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
class VoiceCloneView(FormView):
    template_name = "pages/voice-cloning.html"
    form_class = VoiceCloneForm

    def form_valid(self, form):
        voice: UploadedFile = form.cleaned_data["voice"]
        text = form.cleaned_data["text"]
        language = form.cleaned_data["language"]
        speaker = form.cleaned_data["speaker"]
        speed = form.cleaned_data["speed"]

        id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{id}.wav"
        if voice.name:
            filename = "{0}-{id}.{1}".format(
                *os.path.splitext(voice.name), id=id
            )
        voice_path = utils.get_voice_path(filename, "uploads")
        base_path = utils.get_voice_path("base", "temp")
        upload_path = utils.get_media_path(
            "{}.wav".format(os.path.splitext(os.path.basename(filename))[0]),
            "clones",
        )
        os.makedirs(os.path.dirname(voice_path), exist_ok=True)
        os.makedirs(os.path.dirname(base_path), exist_ok=True)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        with open(voice_path, "wb") as f:
            for chunk in voice.chunks():
                f.write(chunk)

        source_se = torch.load(
            f"checkpoints_v2/base_speakers/ses/{speaker}.pth",
            map_location=device,
        )
        model = TTS(language=language, device=device)
        model.tts_to_file(
            text, model.hps.data.spk2id[speaker], base_path, speed=speed
        )
        del model

        tone_color_converter = ToneColorConverter(
            f"{ckpt_converter}/config.json", device=device
        )
        tone_color_converter.load_ckpt(f"{ckpt_converter}/checkpoint.pth")
        target_se, audio_name = se_extractor.get_se(
            filename, tone_color_converter, vad=False
        )
        encode_message = "@MyShell"
        tone_color_converter.convert(
            audio_src_path=base_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=upload_path,
            message=encode_message,
        )
        file_url = utils.get_media_url(os.path.basename(upload_path), "clones")
        return HttpResponse(
            f'<audio controls><source src="{file_url}" type="audio/wav"></audio>'
        )

    def form_invalid(self, form: VoiceCloneForm):
        return HttpResponse(
            f'<p style="color:red;">{form.errors.as_text()}</p>'
        )
