# RAG Document Q&A

Upload a PDF or text file, then ask questions that are answered **only from that document's content** — not from the model's general knowledge. Built as a full-stack project: FastAPI + ChromaDB + HuggingFace embeddings on the backend, React on the frontend, with unit tests on the core retrieval and chunking logic.

**Runs entirely locally and free** — generation via a local Ollama model (llama3.2), embeddings via a local HuggingFace sentence-transformer. No API keys, no per-request cost.

![status](https://img.shields.io/badge/tests-passing-brightgreen)
![python](https://img.shields.io/badge/python-3.11-blue)
![react](https://img.shields.io/badge/react-18-61dafb)
![license](https://img.shields.io/badge/license-MIT-lightgrey)
![local](https://img.shields.io/badge/runs-100%25%20local-success)

## Demo

<!-- Replace with your own screenshot/GIF: upload a doc, ask a question, show the answer with cited sources -->
`[screenshot or GIF goes here — see "Making this interview-ready" below]`

## Why this exists

Most RAG tutorials stop at "it works on my machine." This project focuses on the parts that actually matter in an interview:

- **Grounded answers, not hallucinations** — the system prompt forces the model to say "I don't have enough information" rather than guessing when the retrieved chunks don't answer the question.
- **Word-aware chunking with real overlap**, not a naive character-count split that cuts words in half.
- **Tested business logic** — chunking and the retrieval→generation pipeline are unit tested with fakes/mocks, so tests run in milliseconds with no API key or vector DB required.
- **A real API boundary** — FastAPI backend, React frontend talking over HTTP, not a single notebook.

## Architecture

```
┌─────────────┐      upload file       ┌──────────────┐
│   React UI  │ ──────────────────────▶│   FastAPI    │
│  (Vite)     │                        │   /upload    │
│             │◀────────────────────── │   /ask       │
└─────────────┘      answer + sources  └──────┬───────┘
                                               │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                        chunk_text()    ChromaDB (vector     Ollama
                        (ingest.py)    store, local, embeds  (local LLM,
                                       via HuggingFace)        llama3.2)
```

**Flow:** a document is split into overlapping word-based chunks → each chunk is embedded locally (HuggingFace `all-MiniLM-L6-v2`) and stored in a local ChromaDB collection → a question triggers a similarity search for the top-k relevant chunks → those chunks are passed as context to a local Ollama model, which is instructed to answer only from that context and cite sources.

## Project structure

```
rag-document-qa/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes: /upload, /ask, /health
│   │   ├── ingest.py        # PDF/text loading + chunking (pure, testable)
│   │   ├── vectorstore.py   # ChromaDB wrapper
│   │   ├── rag.py           # retrieval + local LLM generation (Ollama)
│   │   └── config.py        # env-based settings
│   ├── tests/
│   │   ├── test_ingest.py   # chunking logic — no external deps
│   │   └── test_rag.py      # RAG pipeline — mocked store & chat client
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/      # ChatWindow, Message, UploadPanel
├── sample_docs/             # a small doc to test with immediately
└── docker-compose.yml
```

## Running it locally

### 1. Backend

First, install [Ollama](https://ollama.com) and pull the model once:

```bash
ollama pull llama3.2
```

Then:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # defaults work as-is, no API key needed
uvicorn app.main:app --reload
```

The first request will download the `all-MiniLM-L6-v2` embedding model from HuggingFace (one-time, a few hundred MB), then everything runs offline.

Backend runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend.

### 3. Try it

Open the frontend, upload `sample_docs/company_handbook_excerpt.txt`, then ask: *"How many remote days are allowed per week?"* The answer should cite the uploaded file and quote the relevant policy line.

### Docker (backend + Ollama, fully self-contained)

```bash
docker compose up --build
docker exec -it rag-document-qa-ollama-1 ollama pull llama3.2   # one-time, inside the container
```

## Running the tests

```bash
cd backend
python -m unittest discover -s tests -v
```

10 tests, all passing, no Ollama server, API key, or vector database required — the chunking tests use plain Python, and the RAG pipeline tests inject a fake store and a mocked chat client so the logic is verified without a network call.

## Design decisions worth knowing for an interview

- **Why word-based chunking instead of character-based?** Character splits can cut a word in half mid-token, which hurts embedding quality. Splitting on whitespace keeps every chunk made of whole words.
- **Why inject the chat client into `answer_question()` instead of constructing it inside?** Dependency injection — it lets the RAG logic be unit tested with a fake client, so tests don't need a running Ollama server or network access, and run in milliseconds. It also means swapping `ChatOllama` for a hosted model later is a one-line change, not a rewrite.\n- **Why local models instead of a hosted API?** Zero cost, works offline, and no data leaves the machine — a deliberate tradeoff against the higher quality of a larger hosted model, worth stating plainly in an interview rather than hiding it.
- **Why ChromaDB instead of a hosted vector DB?** Zero external setup for a portfolio project — `PersistentClient` just writes to a local folder. Swapping in Pinecone/Weaviate would only mean changing `vectorstore.py`; the rest of the app doesn't know or care which vector DB is behind it.
- **What happens if the document doesn't contain the answer?** The system prompt explicitly instructs the model to say so rather than fall back on general knowledge — tested in `test_answer_question_with_no_matches`.

## Possible extensions

- Streaming responses token-by-token instead of waiting for the full answer
- Multi-document filtering (ask questions scoped to one uploaded file)
- Swap ChromaDB for a hosted vector store for multi-user deployment
- Add conversation memory so follow-up questions resolve pronouns ("what about the second point?")

## License

MIT
