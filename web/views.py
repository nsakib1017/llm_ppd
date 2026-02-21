from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def consent(request):
    return render(request, "consent.html")

def questionnaire(request):
    return render(request, "questionnaire.html")

def history(request):
    return render(request, "history.html")

def chat(request):
    return render(request, "chat.html")

def medication(request):
    return render(request, "medication.html")