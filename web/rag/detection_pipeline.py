import os
import json
from typing import Any, Dict, List, Optional, Tuple

from .retrieve import retrieve
from .llm import call_featherless

INDEX_DIR = "web/rag_index"
print(os.getcwd())


def generate_ppd_score(
    user_text: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    k: int = 10,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    PPD detection + scoring RAG pipeline.

    Inputs:
      - user_text: current user message (free text symptoms, mood journal, etc.)
      - chat_history: optional list like [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
    Returns:
      - (result_json, rag_results)

    result_json format (expected):
      {
        "category": "CategoryNameOrLevel",
        "category_id": 0-4,
        "score": 0-100,
        "confidence": 0.0-1.0,
        "rationale": "short explanation",
        "evidence": [{"quote":"...", "citation":"[src p.page]"}],
        "missing_info": ["..."],
        "follow_up_questions": ["..."],
        "safety_flag": {"risk": "none|urgent", "reason": "...", "recommended_action": "..."}
      }
    """
    user_text = (user_text or "").strip()
    if not user_text:
        return (
            {
                "error": "empty_input",
                "message": "Please provide symptoms, thoughts/feelings, or context so I can assess PPD risk.",
            },
            [],
        )

    # Retrieval query tuned to pull:
    # - the symptoms->category dataset chunk(s)
    # - category definitions, thresholds, mappings
    # - any clinical guidance text you indexed
    retrieval_query = (
        "postpartum depression symptoms dataset categories mapping thresholds "
        "severity levels five categories rubric + "
        + user_text
    )

    rag_results = retrieve(retrieval_query, INDEX_DIR, k=k)

    # Build a concise RAG block (truncate each chunk to control prompt size)
    rag_lines: List[str] = []
    for r in rag_results:
        src = r.get("meta", {}).get("source", "unknown")
        page = r.get("meta", {}).get("page", "?")
        chunk = (r.get("text") or "")[:1400]
        rag_lines.append(f"[{src} p.{page}] {chunk}")
    rag_block = "\n\n".join(rag_lines)

    # System prompt: make the model behave like a scorer + classifier, not a chatbot
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are a postpartum depression (PPD) risk scoring assistant.\n"
                "Your task is to assign the user to ONE of 5 PPD categories (as defined in the Retrieved Documents) "
                "and produce a calibrated risk score.\n\n"
                "Rules:\n"
                "1) You may use general medical knowledge for context, BUT the 5-category mapping must follow the dataset/rubric "
                "found in the Retrieved Documents whenever available.\n"
                "2) You may cite a source ONLY if that claim is directly supported by the Retrieved Documents.\n"
                "   Use only the exact tags like [source p.page]. Never invent citations.\n"
                "3) Output MUST be valid JSON only (no markdown, no extra text).\n"
                "4) If the user text is insufficient to classify reliably, choose the best category with LOW confidence and "
                "list missing_info + 1–3 follow_up_questions.\n"
                "5) Safety: If the user mentions self-harm, suicidal thoughts, harm to baby, psychosis, or immediate danger, "
                "set safety_flag.risk='urgent' and recommend urgent local help.\n"
                "6) You are not diagnosing; you are providing risk stratification and recommending next steps.\n"
            ),
        }
    ]

    if chat_history:
        # For scoring, we only need recent context; but keep as-is if you want full history.
        messages.extend(chat_history)

    # User prompt: enforce the exact output schema and evidence behavior
    messages.append(
        {
            "role": "user",
            "content": (
                "Use the Retrieved Documents to identify the 5 PPD categories and their symptom patterns/criteria.\n"
                "Then classify the USER into exactly ONE category and produce a score.\n\n"
                "Scoring guidance:\n"
                "- score is 0–100 (higher = higher risk/severity).\n"
                "- confidence is 0.0–1.0.\n"
                "- category_id must be an integer 0–4 (0=lowest severity, 4=highest severity) unless the dataset defines a different ordering; "
                "if the dataset defines ordering differently, follow it and explain in rationale.\n\n"
                "Evidence rules:\n"
                "- Include up to 5 evidence items.\n"
                "- Each evidence item must include a short quote and its exact citation tag.\n"
                "- If the docs do not define categories clearly, set confidence <= 0.4 and explain what is missing.\n\n"
                "Return JSON with exactly these keys:\n"
                "{\n"
                '  "category": string,\n'
                '  "category_id": integer,\n'
                '  "score": number,\n'
                '  "confidence": number,\n'
                '  "rationale": string,\n'
                '  "evidence": [{"quote": string, "citation": string}],\n'
                '  "missing_info": [string],\n'
                '  "follow_up_questions": [string],\n'
                '  "safety_flag": {"risk": "none"|"urgent", "reason": string, "recommended_action": string}\n'
                "}\n\n"
                f"USER_TEXT:\n{user_text}\n\n"
                "Retrieved Documents:\n"
                f"{rag_block if rag_block else '(none)'}\n"
            ),
        }
    )

    raw_reply = call_featherless(messages)

    # Try parsing strict JSON. If the model returns extra text, do a best-effort extraction.
    result: Dict[str, Any]
    try:
        result = json.loads(raw_reply)
    except Exception:
        # Best-effort: extract first JSON object substring
        start = raw_reply.find("{")
        end = raw_reply.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                result = json.loads(raw_reply[start : end + 1])
            except Exception:
                result = {
                    "error": "invalid_json_from_model",
                    "raw_reply": raw_reply,
                }
        else:
            result = {
                "error": "invalid_json_from_model",
                "raw_reply": raw_reply,
            }

    return result, rag_results