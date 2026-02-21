from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return render(request, 'web/home.html')

def consent(request):
    return HttpResponse("<h1>Consent</h1><p>Consent page.</p>")

def questioneer(request):
    return render(request, 'web/questioneer.html')

def daily_meds(request):
    return render(request, 'web/daily_meds.html')

def mood_statistics(request):
    return render(request, 'web/mood_statistics.html')

def materna_ai(request):
    return render(request, 'web/materna_ai.html')