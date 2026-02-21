from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import requests
from .rag.llm import call_featherless   
import json

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .rag.llm import call_featherless   # ← import your function

SESSION_KEY = "chat_messages"


def _get_messages(request):
    msgs = request.session.get(SESSION_KEY, [])
    if not isinstance(msgs, list):
        msgs = []
    return msgs


def _set_messages(request, msgs):
    request.session[SESSION_KEY] = msgs
    request.session.modified = True


@require_http_methods(["GET", "POST"])
def chat(request):
    messages = _get_messages(request)
    error = None

    if request.method == "POST":
        user_text = (request.POST.get("message") or "").strip()
        if not user_text:
            return redirect("chat")

        # Add user message
        messages.append({
            "role": "user",
            "content": user_text
        })
        _set_messages(request, messages)

        try:
            # Send full conversation history
            assistant_text = call_featherless(messages)

            # Add assistant reply
            messages.append({
                "role": "assistant",
                "content": assistant_text
            })
            _set_messages(request, messages)

            return redirect("chat")

        except Exception as e:
            error = str(e)

    return render(request, "chat.html", {
        "messages": messages,
        "error": error
    })


@require_http_methods(["POST"])
def chat_clear(request):
    _set_messages(request, [])
    return redirect("chat")




def home(request):
    return render(request, 'home.html')

def consent(request):
    return render(request, 'consent.html')

def questionnaire(request):
    return render(request, 'questionnaire.html')

def medication(request):
    return render(request, 'medication.html')

def history(request):
    return render(request, 'history.html')