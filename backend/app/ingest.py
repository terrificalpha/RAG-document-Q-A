"""Document loading and chunking.

Kept dependency-light and pure-functional where possible, so the
chunking logic can be unit tested without a PDF parser or a vector
database installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    text: str
    source: str
    chunk_index: int


def read_pdf_text(path: str | Path) -> str:
    """Extract raw text from a PDF file using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def read_text_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def load_document(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return read_pdf_text(path)
    return read_text_file(path)


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[Chunk]:
    """Split text into overlapping, word-aware chunks.

    Splitting on whitespace rather than raw characters avoids cutting
    words in half, which keeps embeddings and retrieved snippets
    readable. chunk_overlap must be smaller than chunk_size or this
    raises, since otherwise the window never advances.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    step = chunk_size - chunk_overlap

    while start < len(words):
        window = words[start : start + chunk_size]
        chunk_body = " ".join(window).strip()
        if chunk_body:
            chunks.append(
                Chunk(text=chunk_body, source=source, chunk_index=index)
            )
            index += 1
        start += step

    return chunks


def chunk_document(
    path: str | Path,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[Chunk]:
    path = Path(path)
    text = load_document(path)
    return chunk_text(text, source=path.name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
