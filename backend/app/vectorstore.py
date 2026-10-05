"""Thin wrapper around ChromaDB so the rest of the app depends on a
small interface rather than Chroma's API directly.

Embeddings are generated locally with HuggingFaceEmbeddings
(sentence-transformers under the hood) — no API key, no network
call per embedding, everything runs on your machine.
"""
from __future__ import annotations

from .config import settings
from .ingest import Chunk


class _HuggingFaceEmbeddingFunction:
    """Adapts LangChain's HuggingFaceEmbeddings to the plain callable
    interface ChromaDB's collection expects.
    """

    def __init__(self, model_name: str):
        from langchain_huggingface import HuggingFaceEmbeddings

        self._embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(list(input))

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(list(input))

    def embed_query(self, input: str | list[str]) -> list[float] | list[list[float]]:
        if isinstance(input, list):
            if len(input) == 1:
                return [self._embeddings.embed_query(input[0])]
            return [self._embeddings.embed_query(text) for text in input]
        return self._embeddings.embed_query(input)

    def name(self) -> str:
        return "huggingface-embedding-function"


class VectorStore:
    def __init__(self, persist_dir: str | None = None, embedding_model: str | None = None):
        import chromadb

        self.persist_dir = persist_dir or settings.chroma_dir
        self.embedding_model = embedding_model or settings.embedding_model

        self._client = chromadb.PersistentClient(path=self.persist_dir)
        self._embed_fn = _HuggingFaceEmbeddingFunction(self.embedding_model)
        self._collection = self._client.get_or_create_collection(
            name="documents",
            embedding_function=self._embed_fn,
        )

    def add_chunks(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0

        ids = [f"{c.source}-{c.chunk_index}" for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [{"source": c.source, "chunk_index": c.chunk_index} for c in chunks]

        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(chunks)

    def query(self, question: str, top_k: int | None = None) -> list[dict]:
        top_k = top_k or settings.top_k
        result = self._collection.query(query_texts=[question], n_results=top_k)

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        return [
            {"text": doc, "source": meta.get("source"), "distance": dist}
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

    def document_count(self) -> int:
        return self._collection.count()