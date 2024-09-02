from django import forms
from django.http import HttpResponse
from django.views.generic import FormView


class VoiceCloneForm(forms.Form):
    voice = forms.FileField(
        label="Upload Your Audio File",
        required=True,
        widget=forms.FileInput(
            attrs={"class": "d-none", "id": "voice", "accept": "audio/*"}
        ),
    )
    diffusion = forms.FloatField(
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

    embedding_scale = forms.FloatField(
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


class VoiceCloneView(FormView):
    template_name = "pages/voice-cloning.html"
    form_class = VoiceCloneForm

    def form_valid(self, form):
        voice = form.cleaned_data["voice"]
        diffusion = form.cleaned_data["diffusion"]
        embedding_scale = form.cleaned_data["embedding_scale"]
        alpha = form.cleaned_data["alpha"]
        beta = form.cleaned_data["beta"]

        return HttpResponse(self.request.POST)

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
