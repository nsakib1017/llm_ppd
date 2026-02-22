import os
from typing import Any, Dict, List, Optional, Tuple

from .retrieve import retrieve
from .llm import call_featherless
    
INDEX_DIR = "web/rag_index"
print(os.getcwd())

def generate_ai_reply(
    user_text: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    k: int = 5,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Pure RAG pipeline:
    - user_text: current user input
    - chat_history: list like [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
    Returns: (assistant_reply, rag_results)
    """
    user_text = (user_text or "").strip()
    if not user_text:
        return "Please provide a message.", []

    rag_results = retrieve(user_text, INDEX_DIR, k=k)

    # Build a concise RAG block (truncate each chunk to control prompt size)
    rag_lines = []
    for r in rag_results:
        src = r.get("meta", {}).get("source", "unknown")
        page = r.get("meta", {}).get("page", "?")
        chunk = (r.get("text") or "")[:1200]
        rag_lines.append(f"[{src} p.{page}] {chunk}")
    rag_block = "\n\n".join(rag_lines)

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are a medical information assistant for postpartum mental health support.\n"
                "Follow these rules:\n"
                "1) You may use general medical knowledge to answer the question.\n"
                "2) You may cite a source ONLY if the information is directly supported by the Retrieved Documents.\n"
                "3) Never fabricate citations or sources. Use only the provided [source p.page] tags.\n"
                "4) If the Retrieved Documents do not support an important part of the answer, say so clearly.\n"
                "5) Be safety-conscious: you are not a doctor and you do not diagnose.\n"
                "   If the user mentions self-harm, harm to baby, or immediate danger, advise seeking urgent help.\n"
                "6) Keep responses concise, practical, and empathetic.\n"
                "7) If the question is unclear or evidence is weak, ask 1–2 clarifying questions.\n"
            ),
        }
    ]

    if chat_history:
        messages.extend(chat_history)

    messages.append(
        {
            "role": "user",
            "content": (
                "Answer the QUESTION below.\n\n"
                "Rules for citations:\n"
                "- Cite a source ONLY if the Retrieved Documents support that exact claim.\n"
                "- Use the exact [source p.page] tag when citing.\n"
                "- If the Retrieved Documents do not contain relevant evidence, answer from general knowledge and DO NOT cite.\n\n"
                f"QUESTION:\n{user_text}\n\n"
                "Retrieved Documents (may be empty):\n"
                f"{rag_block if rag_block else '(none)'}\n"
            ),
        }
    )

    reply = call_featherless(messages)
    return reply, rag_results