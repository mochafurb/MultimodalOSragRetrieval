# End-to-End Data Flow

## Offline Pipeline (Document Ingestion)

```text
PDF / PPTX / DOCX / XLSX File
        ↓
parser.py
    → Extracts:
        • TextChunk
        • TableChunk
        • ImageChunk
        ↓
chunker.py
    → Splits content into IndexableChunk
    → ~800 character chunks
    → Adds metadata
        ↓
embedder.py
    → GPT-4o Vision processes images
    → text-embedding-3-large generates embeddings
    → Produces 1536-dimension vectors
        ↓
indexer.py
    → Stores vectors + metadata preview in Pinecone
    → Stores full content + complete metadata in PostgreSQL
````

---

## Online Pipeline (Question Answering)

```text
User asks a DBMS question via the Streamlit UI or REST API
        ↓
api/main.py
    → Receives POST /chat request
    → Retrieves session history from memory
    → Routes to multi-agent middleware
        ↓
agent/multi_agent.py
    → Routes to: ChitchatAgent | RetrievalAgent | CodeGraphAgent
        ↓
api/auth.py
    → Validates API key / Bearer token
        ↓
agent/graph.py
    → Executes the LangGraph state machine
```

---

## LangGraph State Machine

```text
query_rewriter_node
    → GPT-4o rewrites user query into 3–4 optimized search queries
        ↓

retriever_node
    → Parallel Pinecone vector search
    → Retrieves ~20 candidate chunks
        ↓

retrieval_grader_node
    → GPT-4o filters irrelevant chunks
    → Keeps ~10 relevant chunks
        ↓

reranker_node
    → GPT-4o LLM-based reranker scores chunks
    → Selects top 5 chunks
        ↓

context_builder_node
    → Fetches full content from PostgreSQL
    → Builds final retrieval context
        ↓

generator_node
    → GPT-4o generates cited answer using retrieved context
        ↓

reflection_grader_node
    → GPT-4o evaluates response quality
        ↓

[If quality is poor AND retry count < 2]
    → retry_prep
    → Loops back to query_rewriter_node

[If quality is good]
    → END
```

---

## Response Delivery

```text
api/main.py
    → Stores assistant response in memory
    → Returns ChatResponse JSON
        ↓
UI/streamlit_app.py
    → Renders answer with markdown / table / chart
    → Shows citations with source file and page
        ↓
User receives final answer with citations in the chat UI
```
