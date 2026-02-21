from typing import Any, Dict, List, Optional, Tuple

from rag.retrieve import retrieve
from rag.llm import call_featherless

INDEX_DIR = "rag_index"


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
                "You are a helpful assistant.\n"
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
        "role": "system",
        "content": (
            "You are a helpful assistant.\n"
            "- Use the retrieved documents only if they contain relevant information.\n"
            "- If the documents do not contain the answer, say so clearly.\n"
            "- Only include citations [source p.page] for statements that are directly supported by the retrieved text.\n"
            "- If you did not use any retrieved text, do NOT include citations."
        ),
        }
    )

    reply = call_featherless(messages)
    return reply, rag_results