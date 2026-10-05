# Local RAG Document Q&A System

A full-stack Retrieval-Augmented Generation (RAG) web application that lets you upload documents (PDF/TXT) and query them with strict grounding. Answers are generated exclusively from the uploaded file context with source citations, preventing hallucinations.

The application runs **100% locally and offline**:
* **LLM Engine:** Local Ollama (`llama3.2`)
* **Embedding Model:** Local HuggingFace sentence-transformers (`all-MiniLM-L6-v2`)
* **Vector Database:** Local ChromaDB
* **Backend:** FastAPI (Python 3.11)
* **Frontend:** React + Vite (Custom Neon Glassmorphic Interface)

![status](https://img.shields.io/badge/tests-passing-brightgreen)
![python](https://img.shields.io/badge/python-3.11-blue)
![react](https://img.shields.io/badge/react-18-61dafb)
![license](https://img.shields.io/badge/license-MIT-lightgrey)
![local](https://img.shields.io/badge/runs-100%25%20local-success)

---

## Technical Overview & Flow

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (React + Vite)"]
        UI["Chat Interface & Upload Panel"]
    end

    subgraph Backend ["Backend Services (FastAPI)"]
        API["FastAPI App Router"]
        Ingest["Document Loader & Word Chunker"]
        RAG["RAG Retrieval Pipeline"]
    end

    subgraph Storage ["Local Storage & Inference"]
        VectorDB["ChromaDB Vector Store\n(HuggingFace Embeddings)"]
        OllamaEngine["Ollama Inference Engine\n(llama3.2)"]
    end

    UI -->|POST /upload| API
    API --> Ingest
    Ingest -->|Embedded Chunks| VectorDB

    UI -->|POST /ask| API
    API --> RAG
    RAG -->|Similarity Search| VectorDB
    VectorDB -->|Top-k Context| RAG
    RAG -->|Prompt + Chunks| OllamaEngine
    OllamaEngine -->|Grounded Response| RAG
    RAG -->|JSON Response + Sources| UI
