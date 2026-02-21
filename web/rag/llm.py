import os
import requests

from dotenv import load_dotenv
load_dotenv()

FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY")
API_URL = "https://api.featherless.ai/v1/chat/completions"

def call_featherless(messages, model="deepseek-ai/DeepSeek-V3-0324", temperature=0.7, timeout=60):
    if not FEATHERLESS_API_KEY:
        raise RuntimeError(
            "FEATHERLESS_API_KEY is not set. In cmd: set FEATHERLESS_API_KEY=... (or use setx + reopen terminal)."
        )

    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)

    if resp.status_code != 200:
        raise RuntimeError(f"Featherless error HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]