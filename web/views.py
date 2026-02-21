from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Home</h1><p>Welcome.</p>")

def consent(request):
    return HttpResponse("<h1>Consent</h1><p>Consent page.</p>")