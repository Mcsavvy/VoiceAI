from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from uuid import uuid4
from django.views.decorators.http import require_http_methods
from gtts import gTTS
import os


# Create your views here.

class TextToSpeechForm(forms.Form):
    text = forms.CharField(label='Enter Your Text', 
                           max_length=1000, 
                           widget=forms.Textarea(attrs={'class': 'form-control my-3 border', 'id': 'text'}), 
                           required=True,
                           )

def index(request):
    # Show the Form
    form = TextToSpeechForm()
    return render(request, 'tts/index.html', {'form': form})

@require_http_methods(["POST"])
def convert_text(request):
    form = TextToSpeechForm(request.POST)
    if not form.is_valid():
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
    # convert text
    text = form.cleaned_data["text"]
    language = 'en'
    speech = gTTS(text=text, lang=language, slow=False)
    filename = "{}.mp3".format(uuid4())   
    speech.save("tts/static/{}".format(filename))
    return HttpResponse(f'<audio controls><source src="/static/{filename}" type="audio/mpeg"></audio>')
    
