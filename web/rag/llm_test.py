# test_llm.py
from llm import call_featherless

if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "Hello! Reply with exactly 5 words."}
    ]
    reply = call_featherless(messages)
    print("LLM reply:", reply)