from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import requests
import json

SESSION_KEY = "chat_messages"

def _get_messages(request):
    msgs = request.session.get(SESSION_KEY, [])
    if not isinstance(msgs, list):
        msgs = []
    return msgs

def _set_messages(request, msgs):
    request.session[SESSION_KEY] = msgs
    request.session.modified = True

def call_llm_ollama(user_text, history):
    """
    Calls Ollama chat endpoint:
    https://github.com/ollama/ollama/blob/main/docs/api.md
    """
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.1",  # change to whatever you pulled in Ollama
        "messages": history + [{"role": "user", "content": user_text}],
        "stream": False,
    }

    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    # Ollama returns: {"message": {"role": "assistant", "content": "..."} , ...}
    return data["message"]["content"]

@require_http_methods(["GET", "POST"])
def chat(request):
    messages = _get_messages(request)
    error = None

    if request.method == "POST":
        user_text = (request.POST.get("message") or "").strip()
        if not user_text:
            return redirect("chat")

        # append user message
        messages.append({"role": "user", "content": user_text})
        _set_messages(request, messages)

        try:
            assistant_text = call_llm_ollama(user_text, messages[:-1])  # history excludes the last user msg
            messages.append({"role": "assistant", "content": assistant_text})
            _set_messages(request, messages)
        except requests.RequestException as e:
            error = f"LLM request failed: {e}"
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            error = f"LLM response parse failed: {e}"

    return render(request, "chat.html", {
        "messages": messages,
        "error": error,
        "is_sending": False,
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

def chat(request):
    return render(request, 'chat.html')