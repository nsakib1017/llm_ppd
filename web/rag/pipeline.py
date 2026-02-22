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
                "You are a helpful medical healthcare assistant.\n"
                "- Use the retrieved documents when relevant.\n"
                "- If the documents do not contain the answer, say you don't have enough information.\n"
                "- Do not invent citations. Only cite using the provided [source p.page] tags."
            ),
        }
    ]

    if chat_history:
        messages.extend(chat_history)

    messages.append(
        {
            "role": "user",
            "content": (
                "Answer the QUESTION below.\n"
                "If the Retrieved Documents contain relevant info, use them and cite them.\n"
                "If they do not contain relevant info, answer from your general knowledge and DO NOT cite.\n\n"
                f"QUESTION:\n{user_text}\n\n"
                f"Retrieved Documents:\n{rag_block if rag_block else '(none)'}"
            ),
        }
    )

    reply = call_featherless(messages)
    return reply, rag_results