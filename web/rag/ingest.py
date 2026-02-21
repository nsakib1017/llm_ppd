import os
import glob
import pickle
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


@dataclass
class Chunk:
    text: str
    meta: Dict[str, Any]


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


def load_pdf_chunks(pdf_path: str, chunk_size: int = 900, overlap: int = 150) -> List[Chunk]:
    reader = PdfReader(pdf_path)
    out: List[Chunk] = []

    for page_idx, page in enumerate(reader.pages):
        page_text = (page.extract_text() or "").strip()
        for chunk in _chunk_text(page_text, chunk_size=chunk_size, overlap=overlap):
            out.append(
                Chunk(
                    text=chunk,
                    meta={
                        "source": os.path.basename(pdf_path),
                        "page": page_idx + 1,
                    },
                )
            )
    return out


def build_faiss_index(
    chunks: List[Chunk],
    index_dir: str,
    model_name: str = "all-MiniLM-L6-v2",
) -> None:
    os.makedirs(index_dir, exist_ok=True)

    model = SentenceTransformer(model_name)
    texts = [c.text for c in chunks]

    # normalize => cosine similarity via inner product
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(index_dir, "index.faiss"))
    with open(os.path.join(index_dir, "chunks.pkl"), "wb") as f:
        serializable = [{"text": c.text, "meta": c.meta} for c in chunks]
        pickle.dump(serializable, f)


def ingest_pdfs(
    pdf_dir: str = "data/pdfs",
    index_dir: str = "rag_index",
    model_name: str = "all-MiniLM-L6-v2",
    chunk_size: int = 900,
    overlap: int = 150,
) -> Tuple[int, int]:
    pdf_paths = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    all_chunks: List[Chunk] = []

    for p in pdf_paths:
        all_chunks.extend(load_pdf_chunks(p, chunk_size=chunk_size, overlap=overlap))

    if not all_chunks:
        raise RuntimeError(f"No text chunks extracted. Check PDFs in: {pdf_dir}")

    build_faiss_index(all_chunks, index_dir=index_dir, model_name=model_name)
    return len(pdf_paths), len(all_chunks)


if __name__ == "__main__":
    pdfs, chunks = ingest_pdfs()
    print(f"Ingested {pdfs} PDFs into {chunks} chunks. Index saved to rag_index/")