"""
agent/tools.py
───────────────
Retrieval tools for the LangGraph agent.

Tools:
  1. hybrid_retrieval        – OpenAI embedding semantic search via Pinecone (text/image namespaces)
  2. colpali_retrieval       – ColPali page-level visual search via Pinecone (colpali namespace)
  3. fetch_full_chunk        – Fetch full chunk text from Postgres by chunk_id
  4. fetch_colpali_page      – Fetch page image + metadata from Postgres by page_id
  5. metadata_filter_search  – SQL filter on Postgres for structured facets

At query time, hybrid_retrieval and colpali_retrieval are both called.
Results are merged in the retriever node — chunk hits give granular citations,
ColPali hits provide page images for GPT-4o visual context.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import structlog
from pinecone import Pinecone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config.settings import get_settings
from ingestion.embedder import Embedder

settings = get_settings()
log = structlog.get_logger()

# ── Singletons ────────────────────────────────────────────────────────────────
_pinecone_text_index   = None
_pinecone_colpali_index = None
_engine                = None
_embedder              = None
_colpali_embedder      = None
_local_chunks_cache: dict[str, dict] | None = None


def _get_local_chunks() -> dict[str, dict]:
    global _local_chunks_cache
    if _local_chunks_cache is None:
        _local_chunks_cache = {}
        try:
            from ingestion.parser import DocumentParser
            from ingestion.chunker import DocumentChunker
            parser = DocumentParser()
            chunker = DocumentChunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
            data_dir = Path(__file__).resolve().parent.parent / "data"
            if data_dir.exists():
                for f in sorted(data_dir.glob("*.pdf")):
                    try:
                        parsed = parser.parse(f)
                        chunks = chunker.chunk_document(parsed)
                        for c in chunks:
                            _local_chunks_cache[c.chunk_id] = {
                                "chunk_id": c.chunk_id,
                                "kind": c.kind,
                                "content": c.content,
                                "source_file": c.metadata.get("source_file", f.name),
                                "doc_type": c.metadata.get("doc_type", "pdf"),
                                "page_or_slide": c.metadata.get("page_or_slide", 1),
                                "section_title": c.metadata.get("section_title", ""),
                                "doc_id": c.metadata.get("doc_id", ""),
                                "topic": c.metadata.get("topic", ""),
                                "domain": c.metadata.get("domain", ""),
                                "metadata": c.metadata,
                                "content_preview": c.content[:500],
                            }
                    except Exception as exc:
                        log.warning("Local parse error", file=str(f), error=str(exc))
        except Exception as exc:
            log.warning("Local chunk loading failed", error=str(exc))
    return _local_chunks_cache


def _local_search(query: str, top_k: int = 20) -> list[dict]:
    chunks = _get_local_chunks()
    if not chunks:
        return []
    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
    if not words:
        words = query.lower().split()
    scored = []
    for cid, c in chunks.items():
        text_lower = (c["content"] + " " + c.get("section_title", "") + " " + c["source_file"]).lower()
        score = sum(text_lower.count(w) for w in words)
        if words and all(w in text_lower for w in words):
            score += 10
        if score > 0:
            scored.append({
                "chunk_id": cid,
                "score": float(score),
                "source": "local_fallback",
                "namespace": "text",
                "metadata": c["metadata"],
                "content_preview": c["content_preview"],
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def _get_pinecone_text():
    global _pinecone_text_index
    if _pinecone_text_index is None:
        pc = Pinecone(api_key=settings.pinecone_api_key)
        _pinecone_text_index = pc.Index(settings.pinecone_index_name)
    return _pinecone_text_index


def _get_pinecone_colpali():
    global _pinecone_colpali_index
    if _pinecone_colpali_index is None:
        pc = Pinecone(api_key=settings.pinecone_api_key)
        colpali_index_name = f"{settings.pinecone_index_name}-colpali"
        _pinecone_colpali_index = pc.Index(colpali_index_name)
    return _pinecone_colpali_index


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url)
    return _engine


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def _get_colpali_embedder():
    global _colpali_embedder
    if _colpali_embedder is None:
        try:
            from ingestion.colpali_embedder import ColPaliEmbedder
            _colpali_embedder = ColPaliEmbedder()
        except Exception:
            return None
    return _colpali_embedder


def _is_pinecone_configured() -> bool:
    key = settings.pinecone_api_key
    return bool(key and key != "mock-key" and not key.startswith("mock") and len(key) > 10)


# ── Tool 1: Hybrid Retrieval ──────────────────────────────────────────────────

async def hybrid_retrieval(
    query: str,
    top_k: int = 20,
    filters: dict | None = None,
    include_images: bool = True,
) -> list[dict]:
    """
    Semantic search via OpenAI embeddings across Pinecone text + image namespaces.
    Gracefully falls back to local document search if Pinecone is unavailable.
    """
    if not _is_pinecone_configured():
        return _local_search(query, top_k)

    try:
        embedder = _get_embedder()
        index    = _get_pinecone_text()

        query_embedding = await embedder.embed_query(query)
        results = []

        # Text namespace
        text_response = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=settings.pinecone_namespace_text,
            filter=filters or {},
            include_metadata=True,
        )
        for match in text_response.matches:
            results.append({
                "chunk_id":        match.id,
                "score":           match.score,
                "source":          "hybrid_text",
                "namespace":       "text",
                "metadata":        match.metadata,
                "content_preview": match.metadata.get("content_preview", ""),
            })

        # Image namespace
        if include_images:
            img_response = index.query(
                vector=query_embedding,
                top_k=max(top_k // 2, 3),
                namespace=settings.pinecone_namespace_image,
                filter=filters or {},
                include_metadata=True,
            )
            for match in img_response.matches:
                results.append({
                    "chunk_id":        match.id,
                    "score":           match.score,
                    "source":          "hybrid_image",
                    "namespace":       "image",
                    "metadata":        match.metadata,
                    "content_preview": match.metadata.get("content_preview", ""),
                })

        if results:
            seen: dict[str, dict] = {}
            for r in results:
                cid = r["chunk_id"]
                if cid not in seen or r["score"] > seen[cid]["score"]:
                    seen[cid] = r
            return sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    except Exception as exc:
        log.warning("Pinecone retrieval failed, using local document fallback", error=str(exc))

    return _local_search(query, top_k)


# ── Tool 2: ColPali Retrieval (new) ───────────────────────────────────────────

async def colpali_retrieval(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
) -> list[dict]:
    """
    Page-level visual retrieval via ColPali embeddings.
    Returns page-level results (not chunks) — used to fetch full page
    images for GPT-4o visual context in the generator.

    Falls back to empty list if ColPali is disabled or not available.
    """
    import asyncio

    # Respect the COLPALI_ENABLED flag — never load the heavy model at query
    # time when ColPali is turned off (avoids a 5GB CPU model load + timeout).
    if not settings.colpali_enabled:
        return []

    colpali_emb = _get_colpali_embedder()
    if colpali_emb is None:
        return []   # ColPali not available, degrade gracefully

    try:
        index = _get_pinecone_colpali()
    except Exception:
        return []

    # ColPali query embedding (sync — run in thread pool)
    loop = asyncio.get_event_loop()
    query_vector = await loop.run_in_executor(
        None, colpali_emb.embed_query, query
    )

    response = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace="colpali_pages",
        filter=filters or {},
        include_metadata=True,
    )

    return [
        {
            "page_id":      m.id,
            "score":        m.score,
            "source":       "colpali",
            "source_file":  m.metadata.get("source_file", ""),
            "doc_type":     m.metadata.get("doc_type", ""),
            "page_idx":     m.metadata.get("page_idx", 0),
            "doc_id":       m.metadata.get("doc_id", ""),
            "topic":        m.metadata.get("topic", ""),
            "domain":       m.metadata.get("domain", ""),
        }
        for m in response.matches
    ]


# ── Tool 3: Fetch Full Chunk ──────────────────────────────────────────────────

async def fetch_full_chunk(chunk_id: str) -> dict | None:
    """Retrieve full chunk content from Postgres by chunk_id, or fallback to local cache."""
    try:
        engine = _get_engine()
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text("SELECT * FROM chunks WHERE chunk_id = :cid"),
                {"cid": chunk_id},
            )
            row = result.mappings().first()
            if row:
                return dict(row)
    except Exception as exc:
        log.debug("Postgres fetch_full_chunk failed, checking local cache", error=str(exc))

    return _get_local_chunks().get(chunk_id)


# ── Tool 4: Fetch ColPali Page ────────────────────────────────────────────────

async def fetch_colpali_page(page_id: str) -> dict | None:
    """
    Retrieve full page image + metadata from Postgres colpali_pages table.
    Returns dict with page_image_b64 (PNG) for passing to GPT-4o.
    """
    engine = _get_engine()
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT * FROM colpali_pages WHERE page_id = :pid"),
            {"pid": page_id},
        )
        row = result.mappings().first()
    return dict(row) if row else None


# ── Tool 5: Metadata Filter Search ────────────────────────────────────────────

async def metadata_filter_search(
    query_text: str,
    domain: str | None = None,
    topic: str | None = None,
    doc_type: str | None = None,
    year: int | None = None,
    doc_id: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Full-text search + metadata filter on PostgreSQL."""
    engine = _get_engine()

    conditions = ["content ILIKE :query_pattern"]
    params: dict[str, Any] = {"query_pattern": f"%{query_text}%", "limit": limit}

    if domain:
        conditions.append("domain ILIKE :domain")
        params["domain"] = domain
    if topic:
        conditions.append("topic ILIKE :topic")
        params["topic"] = topic
    if doc_type:
        conditions.append("doc_type = :doc_type")
        params["doc_type"] = doc_type
    if year:
        conditions.append("year = :year")
        params["year"] = year
    if doc_id:
        conditions.append("doc_id = :doc_id")
        params["doc_id"] = doc_id

    where = " AND ".join(conditions)
    sql = f"""
        SELECT chunk_id, kind, content, source_file, doc_type,
               page_or_slide, section_title, doc_id,
               topic, domain, year
        FROM chunks
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT :limit
    """
    async with AsyncSession(engine) as session:
        result = await session.execute(text(sql), params)
        rows   = result.mappings().all()

    return [dict(row) for row in rows]
