from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('I am ready')

def text_to_speech(request):
    return HttpResponse('text to speech is here')
