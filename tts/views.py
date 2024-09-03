from uuid import uuid4

from django import forms
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from app.decorators import login_required

# Create your views here.


class TextToSpeechForm(forms.Form):
    text = forms.CharField(
        label="Enter Your Text",
        max_length=1000,
        widget=forms.Textarea(
            attrs={"class": "form-control my-3 border", "id": "text"}
        ),
        required=True,
    )


@method_decorator([login_required], name="dispatch")
class TextToSpeechView(FormView):
    template_name = "pages/tts.html"
    form_class = TextToSpeechForm

    def form_valid(self, form):
        text = form.cleaned_data["text"]
        language = "en"
        # speech = gTTS(text=text, lang=language, slow=False)
        filename = "{}.mp3".format(uuid4())
        # speech.save("tts/static/{}".format(filename))
        return HttpResponse(
            f'<audio controls><source src="/static/{filename}" type="audio/mpeg"></audio>'
        )

    def form_invalid(self, form):
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
