import os
import glob
import csv
import pickle
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

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


# ---------- PDF ----------
def load_pdf_chunks(pdf_path: str, chunk_size: int = 900, overlap: int = 150) -> List[Chunk]:
    reader = PdfReader(pdf_path)
    out: List[Chunk] = []

    for page_idx, page in enumerate(reader.pages):
        page_text = (page.extract_text() or "").strip()
        for chunk in _chunk_text(page_text, chunk_size=chunk_size, overlap=overlap):
            out.append(
                Chunk(
                    text=chunk,
                    meta={"source": os.path.basename(pdf_path), "type": "pdf", "page": page_idx + 1},
                )
            )
    return out


# ---------- TXT / MD ----------
def load_textfile_chunks(path: str, chunk_size: int = 900, overlap: int = 150) -> List[Chunk]:
    out: List[Chunk] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    for chunk in _chunk_text(text, chunk_size=chunk_size, overlap=overlap):
        out.append(
            Chunk(
                text=chunk,
                meta={"source": os.path.basename(path), "type": "text"},
            )
        )
    return out


# ---------- CSV ----------
def _row_to_text(row: Dict[str, Any], columns: Optional[List[str]] = None) -> str:
    """
    Turn a CSV row into a readable text block.
    Keeping structure helps retrieval a lot more than converting to PDF.
    """
    cols = columns or list(row.keys())
    lines = []
    for c in cols:
        v = row.get(c, "")
        # Normalize whitespace
        v = str(v).strip().replace("\n", " ")
        lines.append(f"{c}: {v}")
    return "\n".join(lines)


def load_csv_chunks(
    csv_path: str,
    chunk_size: int = 900,
    overlap: int = 150,
    max_rows: Optional[int] = None,
) -> List[Chunk]:
    out: List[Chunk] = []

    with open(csv_path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []

        for i, row in enumerate(reader, start=1):
            if max_rows is not None and i > max_rows:
                break

            row_text = _row_to_text(row, columns=columns)

            # Usually one row fits, but we chunk anyway if huge cells exist
            for chunk in _chunk_text(row_text, chunk_size=chunk_size, overlap=overlap):
                out.append(
                    Chunk(
                        text=chunk,
                        meta={
                            "source": os.path.basename(csv_path),
                            "type": "csv",
                            "row": i,
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

    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(index_dir, "index.faiss"))

    # Save as plain dicts (avoid pickle class-path issues)
    with open(os.path.join(index_dir, "chunks.pkl"), "wb") as f:
        serializable = [{"text": c.text, "meta": c.meta} for c in chunks]
        pickle.dump(serializable, f)


def ingest_docs(
    data_dir: str = "data/pdfs",
    index_dir: str = "rag_index",
    model_name: str = "all-MiniLM-L6-v2",
    chunk_size: int = 900,
    overlap: int = 150,
    csv_max_rows: Optional[int] = None,
) -> Tuple[int, int]:
    """
    Ingest PDFs + CSVs + TXT/MD into one shared vector index.
    """
    pdf_paths = sorted(glob.glob(os.path.join(data_dir, "*.pdf")))
    csv_paths = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    txt_paths = sorted(glob.glob(os.path.join(data_dir, "*.txt")))
    md_paths = sorted(glob.glob(os.path.join(data_dir, "*.md")))

    all_chunks: List[Chunk] = []

    for p in pdf_paths:
        all_chunks.extend(load_pdf_chunks(p, chunk_size=chunk_size, overlap=overlap))

    for p in csv_paths:
        all_chunks.extend(load_csv_chunks(p, chunk_size=chunk_size, overlap=overlap, max_rows=csv_max_rows))

    for p in txt_paths + md_paths:
        all_chunks.extend(load_textfile_chunks(p, chunk_size=chunk_size, overlap=overlap))

    if not all_chunks:
        raise RuntimeError(f"No text chunks extracted. Check files in: {data_dir}")

    build_faiss_index(all_chunks, index_dir=index_dir, model_name=model_name)

    num_files = len(pdf_paths) + len(csv_paths) + len(txt_paths) + len(md_paths)
    return num_files, len(all_chunks)


if __name__ == "__main__":
    n_files, n_chunks = ingest_docs()
    print(f"Ingested {n_files} files into {n_chunks} chunks. Index saved to {os.path.abspath('rag_index')}")