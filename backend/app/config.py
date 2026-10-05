"""Central configuration, loaded from environment variables.

Fully local stack: no API keys required. Generation runs through a
local Ollama server, embeddings through a local HuggingFace model.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "llama3.2")
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    chroma_dir: str = os.environ.get("CHROMA_DIR", "./chroma_store")
    chunk_size: int = int(os.environ.get("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.environ.get("CHUNK_OVERLAP", "150"))
    top_k: int = int(os.environ.get("TOP_K", "4"))
    max_upload_mb: int = int(os.environ.get("MAX_UPLOAD_MB", "20"))


settings = Settings()
