"""Retrieval-augmented generation: fetch relevant chunks, then ask a
local LLM (via Ollama) to answer grounded in them.

Runs fully offline once the model is pulled — no API key, no cost
per request.
"""
from __future__ import annotations

from .config import settings

SYSTEM_PROMPT = (
    "You are a precise document question-answering assistant. "
    "Answer ONLY using the provided context. If the context does "
    "not contain the answer, say you don't have enough information "
    "in the documents rather than guessing. Cite the source file "
    "name for each claim when possible."
)


def build_context(retrieved: list[dict]) -> str:
    if not retrieved:
        return "(no relevant context found)"

    parts = []
    for item in retrieved:
        parts.append(f"[source: {item['source']}]\n{item['text']}")
    return "\n\n---\n\n".join(parts)


def _default_client():
    from langchain_ollama import ChatOllama

    return ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)


def answer_question(question: str, store, client=None, model: str | None = None) -> dict:
    """Retrieve context from `store` and generate an answer.

    `client` is injected (an object with an `.invoke(messages)` method
    returning something with a `.content` attribute, matching
    LangChain's chat model interface) so this function is testable
    with a fake instead of a live Ollama server. `store` must
    implement `.query()`.
    """
    retrieved = store.query(question)
    context = build_context(retrieved)

    if client is None:
        client = _default_client()

    # (role, content) tuples are accepted by LangChain chat models
    # without needing to import the BaseMessage classes here, which
    # keeps this module importable (and testable with a plain fake)
    # even when langchain_core isn't installed.
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Context:\n{context}\n\nQuestion: {question}"),
    ]

    response = client.invoke(messages)
    answer_text = response.content

    return {
        "answer": answer_text,
        "sources": sorted({item["source"] for item in retrieved}),
        "chunks_used": len(retrieved),
    }
