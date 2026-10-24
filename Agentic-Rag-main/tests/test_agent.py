"""
tests/test_agent.py
────────────────────
Unit and integration tests for the OS databse rag retrieval pipeline.

Run with:
    pytest tests/test_agent.py -v
    pytest tests/test_agent.py -v -k "unit"   # fast tests only
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.nodes import (
    AgentState,
    context_builder_node,
    generator_node,
    query_rewriter_node,
    retrieval_grader_node,
    reranker_node,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def base_state(**overrides) -> AgentState:
    state: AgentState = {
        "question":          "How does the Linux Completely Fair Scheduler (CFS) calculate virtual runtime (vruntime)?",
        "chat_history":      [],
        "rewritten_queries": [],
        "raw_chunks":        [],
        "graded_chunks":     [],
        "reranked_chunks":   [],
        "full_chunks":       [],
        "citations":         [],
        "context":           "",
        "answer":            "",
        "final_answer":      "",
        "reflection_loops":  0,
        "reflection_result": {},
    }
    state.update(overrides)
    return state


MOCK_CHUNK = {
    "chunk_id":        "os_sched_001",
    "score":           0.92,
    "namespace":       "text",
    "content_preview": "The Linux Completely Fair Scheduler (CFS) maintains a red-black tree indexed by each task's virtual runtime (vruntime)...",
    "metadata": {
        "source_file":   "01_OS_Processes_Threads_and_CPU_Scheduling.pdf",
        "doc_type":      "pdf",
        "page_or_slide": 1,
        "section_title": "Linux Completely Fair Scheduler (CFS) Mechanics",
        "domain":        "CPU Scheduling & Concurrency",
        "doc_id":        "OS-SCHED-2024-001",
    },
}

MOCK_FULL_CHUNK = {
    **MOCK_CHUNK,
    **MOCK_CHUNK["metadata"],
    "content": (
        "The Linux Completely Fair Scheduler (CFS) does not use fixed timeslice quantums. Instead, it "
        "maintains a red-black tree indexed by each task's virtual runtime (vruntime). Virtual runtime "
        "tracks normalized CPU execution time: vruntime += delta_exec * (NICE_0_LOAD / task_weight). "
        "A task with nice 0 has weight 1024. The kernel always dispatches the leftmost node."
    ),
    "kind": "text",
}


# ── Unit tests ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.unit
async def test_query_rewriter_generates_queries():
    """Query rewriter should produce multiple diverse queries."""
    mock_response = MagicMock()
    mock_response.content = '["Linux CFS vruntime calculation", "completely fair scheduler red-black tree", "task_struct nice weight cpu time"]'

    with patch("agent.nodes._llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        state  = base_state()
        result = await query_rewriter_node(state)

    assert "rewritten_queries" in result
    assert len(result["rewritten_queries"]) >= 2
    assert state["question"] in result["rewritten_queries"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_query_rewriter_falls_back_on_bad_json():
    """Query rewriter should include original question if LLM returns bad JSON."""
    mock_response = MagicMock()
    mock_response.content = "Some non-JSON response from LLM"

    with patch("agent.nodes._llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        result = await query_rewriter_node(base_state())

    assert base_state()["question"] in result["rewritten_queries"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_retrieval_grader_filters_irrelevant():
    """Retrieval grader passes through top candidate chunks bounded by rerank_top_n."""
    chunks = [{**MOCK_CHUNK, "chunk_id": f"chunk_{i}"} for i in range(12)]
    result = await retrieval_grader_node(base_state(raw_chunks=chunks))
    assert len(result["graded_chunks"]) <= 8
    assert len(result["graded_chunks"]) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_context_builder_assembles_context():
    """Context builder should format chunks into a readable context string."""
    with patch("agent.nodes.fetch_full_chunk", new_callable=AsyncMock) as mock_fetch, \
         patch("agent.nodes.fetch_colpali_page", new_callable=AsyncMock) as mock_colpali:
        mock_fetch.return_value = MOCK_FULL_CHUNK
        mock_colpali.return_value = None
        result = await context_builder_node(
            base_state(reranked_chunks=[MOCK_CHUNK])
        )

    assert "context" in result
    assert "CFS" in result["context"] or "vruntime" in result["context"]
    assert len(result["citations"]) == 1
    assert result["citations"][0]["source_file"] == MOCK_FULL_CHUNK["source_file"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generator_uses_context():
    """Generator should produce a non-empty answer using the provided context."""
    mock_response = MagicMock()
    mock_response.content = (
        "The Linux CFS scheduler indexes tasks by virtual runtime (vruntime) in a red-black tree, "
        "advancing vruntime proportionally based on nice priority weights."
    )

    with patch("agent.nodes._llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        result = await generator_node(
            base_state(context="CFS scheduling context here...")
        )

    assert result["answer"]
    assert "CFS" in result["answer"] or "vruntime" in result["answer"]


# ── Integration tests (require real API keys) ─────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_pipeline_scheduling_query():
    """
    End-to-end test of the full LangGraph pipeline.
    Requires real Pinecone, OpenAI API keys.
    Run with: pytest -m integration
    """
    from agent.graph import build_graph

    graph = build_graph()
    result = await graph.ainvoke(base_state(
        question="How does the Linux CFS algorithm prevent process starvation?"
    ))

    assert result.get("final_answer") or result.get("answer")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_pipeline_memory_query():
    """Test Virtual memory and paging query."""
    from agent.graph import build_graph

    graph  = build_graph()
    result = await graph.ainvoke(base_state(
        question="Explain multi-level paging and how TLB reduces memory translation latency."
    ))
    assert result.get("final_answer") or result.get("answer")
