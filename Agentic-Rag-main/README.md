# OS databse rag retrieval — Agentic RAG System

An advanced, production-grade **Retrieval-Augmented Generation (RAG)** system built for Operating Systems (OS) knowledge and systems architecture retrieval. The system uses a multi-agent LangGraph architecture to answer technical OS questions with precise citations from a curated reference library.

---

## Overview

This system indexes 7 comprehensive Operating Systems reference documents covering the full spectrum of kernel and systems internals — from process management and CPU scheduling through virtual memory, paging, concurrency, deadlocks, file systems, kernel architecture, IPC, and container virtualization.

Users can ask natural language questions and receive accurate, cited answers grounded in the Operating Systems knowledge base. The system supports:
- Plain text answers with inline citations
- Auto-rendered markdown tables for structured comparisons
- AI-generated charts from numeric benchmark data in the documents
- Multi-turn conversation with session memory
- Stop generation mid-response

---

## Knowledge Base

| # | Document | Topics Covered |
|---|----------|---------------|
| 1 | `01_OS_Processes_Threads_and_CPU_Scheduling.pdf` | PCB, Context Switching, Linux CFS, vruntime, MLFQ, Round Robin |
| 2 | `02_OS_Memory_Management_and_Virtual_Memory.pdf` | 4-Level Paging, TLB, Page Faults, LRU, Clock, Belady's Anomaly, Thrashing |
| 3 | `03_OS_Concurrency_Synchronization_and_Deadlocks.pdf` | Mutex, Semaphores, Peterson's Algorithm, Coffman conditions, Banker's Algorithm |
| 4 | `04_OS_Storage_File_Systems_and_Disk_IO.pdf` | Inodes, Extents, VFS, Directory Entries, Journaling, Disk Scheduling |
| 5 | `05_OS_Kernel_Architecture_Syscalls_and_Security.pdf` | Monolithic vs Microkernels, Dual-Mode Ring 0/3, Syscalls, ASLR, DEP, LSM |
| 6 | `06_OS_Interprocess_Communication_and_Distributed_OS.pdf` | Pipes, POSIX Shared Memory, UNIX Domain Sockets, RPC, Network IPC |
| 7 | `07_OS_Virtualization_Containers_and_Resource_Isolation.pdf` | Type 1 vs 2 Hypervisors, Linux cgroups v2, Namespaces, OverlayFS |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│             UI/streamlit_app.py                         │
└─────────────────────┬───────────────────────────────────┘
                      │ POST /chat
┌─────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                         │
│               api/main.py  (v2.1.0)                    │
│   /chat  /chat/stop  /chat/reset  /documents  /ingest   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│            Multi-Agent Router                           │
│           agent/multi_agent.py                          │
│  ┌───────────────┬─────────────────┬──────────────────┐ │
│  │ ChitchatAgent │ RetrievalAgent  │ CodeGraphAgent   │ │
│  │  (GPT-4o-mini)│  (LangGraph)    │  (chart gen)     │ │
│  └───────────────┴────────┬────────┴──────────────────┘ │
└───────────────────────────┼─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│              LangGraph State Machine                    │
│                agent/graph.py                           │
│                                                         │
│  query_rewriter → retriever → grader → reranker →      │
│  context_builder → generator → reflection → END         │
└──────────┬──────────────────────┬───────────────────────┘
           │                      │
┌──────────▼──────────┐  ┌───────▼────────────┐
│   Pinecone           │  │    PostgreSQL       │
│  (vector index)      │  │  (full content +   │
│  os-rag-openai       │  │   metadata)        │
└─────────────────────┘  └────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | GPT-4o / GPT-4o-mini / OpenRouter |
| Embeddings | `text-embedding-3-large` (1536d) |
| Vector Store | Pinecone (`dbms-rag-openai` / `os-rag-openai` index) with local fallback |
| Metadata Store | PostgreSQL (via SQLAlchemy async) |
| Orchestration | LangGraph (state machine) |
| Backend API | FastAPI + SSE streaming |
| Frontend | Streamlit |
| PDF Parsing | PyMuPDF (fitz) |
| Optional Multimodal | ColPali (image/chart embeddings) |

---

## Project Structure

```
Agentic-Rag-main/
├── agent/
│   ├── graph.py            # LangGraph state machine definition
│   ├── nodes.py            # All 8 agent node functions
│   ├── multi_agent.py      # Multi-agent router (chitchat/retrieval/chart)
│   ├── prompts.py          # All LLM prompt templates (OS domain)
│   ├── memory.py           # Session memory (PostgreSQL-backed)
│   ├── tools.py            # Pinecone retrieval + local PDF chunk fallback
│   └── cancellation.py     # Stop-generation token registry
├── api/
│   ├── main.py             # FastAPI app ("OS databse rag retrieval")
│   ├── schemas.py          # Pydantic request/response models
│   └── auth.py             # API key / Bearer auth
├── ingestion/
│   ├── parser.py           # PDF/DOCX/PPTX/XLSX parser (PyMuPDF)
│   ├── chunker.py          # Text splitting + chunk ID generation
│   ├── embedder.py         # OpenAI embedding + GPT-4o image captions
│   ├── indexer.py          # Pinecone + PostgreSQL writer
│   ├── metadata_extractor.py  # Metadata extraction
│   └── doc_registry.py     # SHA-256 file-level dedup
├── config/
│   └── settings.py         # Pydantic settings (env-driven)
├── scripts/
│   ├── generate_os_docs.py    # Generates the 7 OS reference PDFs
│   ├── ingest.py              # Full ingestion pipeline CLI
│   └── os_documents_manifest.json
├── data/                   # 7 Operating Systems reference PDFs
├── UI/
│   ├── streamlit_app.py    # Chat UI ("OS databse rag retrieval")
│   └── graph.py            # Matplotlib IPC benchmark chart
├── tests/
│   ├── test_agent.py       # Unit + integration tests (OS fixtures)
│   ├── test_ingestion.py   # Parser + chunker tests
│   └── sample_questions.md # Tiered OS test questions
├── docker-compose.yml      # PostgreSQL + API services
├── .env.example            # Environment variable template
├── graph.md                # End-to-end data flow documentation
└── Sample_questions.md     # 30 sample OS questions for manual testing
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

### 3. Generate OS Reference PDFs

```bash
python scripts/generate_os_docs.py
```

This creates the 7 Operating Systems reference PDFs in `data/`.

### 4. Start the API

```bash
uvicorn api.main:app --reload
```

### 5. Launch the UI

```bash
streamlit run UI/streamlit_app.py
```

---

## Running Tests

```bash
# Unit tests (no API keys needed)
pytest tests/test_agent.py -v -k "unit"

# Ingestion tests (uses data/ PDFs)
pytest tests/test_ingestion.py -v
```

---

## Sample Questions

See [`Sample_questions.md`](Sample_questions.md) for 30 sample questions organised by:
- Basic fact retrieval
- Table generation
- Chart generation
- Follow-up / multi-turn
- Comparison / synthesis
- Chitchat / meta
- Out-of-scope (boundary testing)

---

## License

MIT License.