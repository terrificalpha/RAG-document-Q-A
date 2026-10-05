"""FastAPI app exposing document upload and question-answering."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .ingest import chunk_document
from .rag import answer_question
from .vectorstore import VectorStore

app = FastAPI(
    title="RAG Document Q&A",
    description="Upload documents and ask questions answered only from their content.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend's origin before shipping publicly
    allow_methods=["*"],
    allow_headers=["*"],
)

_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks_used: int


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    total_documents_in_store: int


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    allowed = {".pdf", ".txt", ".md"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Allowed: {sorted(allowed)}")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        chunks = chunk_document(
            tmp_path,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        # Store chunks under the original filename, not the temp path.
        for c in chunks:
            c.source = file.filename

        store = get_store()
        indexed = store.add_chunks(chunks)

        return UploadResponse(
            filename=file.filename,
            chunks_indexed=indexed,
            total_documents_in_store=store.document_count(),
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    if not req.question.strip():
        raise HTTPException(400, "question must not be empty")

    store = get_store()
    if store.document_count() == 0:
        raise HTTPException(409, "No documents indexed yet. Upload one first via /upload.")

    result = answer_question(req.question, store)
    return AskResponse(**result)
