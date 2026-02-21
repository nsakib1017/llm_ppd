import os
import pickle
from typing import Any, Dict, List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Simple in-process cache
_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}


def _load_resources(index_dir: str, model_name: str):
    key = (index_dir, model_name)
    if key in _CACHE:
        return _CACHE[key]["model"], _CACHE[key]["index"], _CACHE[key]["chunks"]

    index_path = os.path.join(index_dir, "index.faiss")
    chunks_path = os.path.join(index_dir, "chunks.pkl")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise RuntimeError(
            f"RAG index not found in '{index_dir}'. Run: python -m rag.ingest (or python rag/ingest.py)"
        )

    model = SentenceTransformer(model_name)
    index = faiss.read_index(index_path)

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    _CACHE[key] = {"model": model, "index": index, "chunks": chunks}
    return model, index, chunks


def retrieve(
    query: str,
    index_dir: str = "rag_index",
    k: int = 5,
    model_name: str = "all-MiniLM-L6-v2",
) -> List[Dict[str, Any]]:
    query = (query or "").strip()
    if not query:
        return []

    model, index, chunks = _load_resources(index_dir, model_name)

    q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    scores, ids = index.search(q, k)

    results: List[Dict[str, Any]] = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        c = chunks[idx]  # now a dict: {"text": ..., "meta": ...}
        results.append({"score": float(score), "text": c["text"], "meta": c["meta"]})
    return results