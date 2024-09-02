from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from uuid import uuid4
from django.views.decorators.http import require_http_methods
from gtts import gTTS
import os
from django.core.files.uploadedfile import UploadedFile


# Create your views here.

class TextToSpeechForm(forms.Form):
    text = forms.CharField(label='Enter Your Text', 
                           max_length=1000, 
                           widget=forms.Textarea(attrs={'class': 'form-control my-3 border', 'id': 'text'}), 
                           required=True,
                           )

class VoiceCloneForm(forms.Form):
    voice = forms.FileField(label='Upload Your Audio File',
                                  required=True,
                                  widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'voice',"accept": "audio/*"}),
                                  )
    diffusion = forms.FloatField(label='Diffusion', 
                                 required=True,
                                 widget=forms.NumberInput(attrs={'type': 'range',
                                                                 'id': 'diffusion',
                                                                 'min': '0',
                                                                 'max': '20',
                                                                 'step': '1',
                                                                 'value': '0',
                                                                 'oninput': 'changeInput(event)'}),
                                
                                 )

    embedding_scale = forms.FloatField(label='Embedding Scale', 
                                        required=True,
                                        widget=forms.NumberInput(attrs={'type': 'range',
                                                                        'id': 'embedding_scale',
                                                                        'min': '0',
                                                                        'max': '10',
                                                                        'step': '1',
                                                                        'value': '0',
                                                                        'oninput': 'changeInput(event)'}),
                                        
                                        )
    
    alpha = forms.FloatField(label='Alpha', 
                            required=True,
                            widget=forms.NumberInput(attrs={'type': 'range',
                                                            'id': 'embedding_scale',
                                                            'min': '0',
                                                            'max': '10',
                                                            'step': '1',
                                                            'value': '0',
                                                            'oninput': 'changeInput(event, 0.1, true)'}),
                            
                            )
    
    beta = forms.FloatField(label='Beta', 
                            required=True,
                            widget=forms.NumberInput(attrs={'type': 'range',
                                                            'id': 'embedding_scale',
                                                            'min': '0',
                                                            'max': '10',
                                                            'step': '1',
                                                            'value': '0',
                                                            'oninput': 'changeInput(event, 0.1, true)'}),
                            
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


def voice_clone(request):
    return render(request, 'tts/voice_clone.html', {'form': VoiceCloneForm()})

@require_http_methods(["POST"])
def handle_voice(request):

    form = VoiceCloneForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(f'<p style="color:red;">{form.errors}</p>')
    # save the uploaded file
    voice: UploadedFile = form.cleaned_data["audio"]
    diffusion = form.cleaned_data["diffusion"]
    embedding_scale = form.cleaned_data["embedding_scale"]
    alpha = form.cleaned_data["alpha"]
    beta = form.cleaned_data["beta"]

    

    return HttpResponse(request.POST)
