"""
tests/test_ingestion.py
────────────────────────
Tests for the document parsing and chunking pipeline.
Uses the actual Operating Systems reference documents in the data/ directory where available.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.chunker import DocumentChunker
from ingestion.parser import DocumentParser, ParsedDocument

DATA_DIR = Path(__file__).parent.parent / "data"

# Resolve actual OS document filenames
def find_os_doc(pattern: str) -> Path | None:
    if DATA_DIR.exists():
        matches = list(DATA_DIR.glob(f"*{pattern}*"))
        return matches[0] if matches else None
    return None


# ── Parser tests ──────────────────────────────────────────────────────────────

class TestDocumentParser:
    parser = DocumentParser()

    def test_parse_pdf_processes_and_scheduling(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available — run scripts/generate_os_docs.py first")
        doc = self.parser.parse(path)
        assert doc.doc_type == "pdf"
        assert len(doc.text_chunks) > 0
        assert any("CFS" in c.text or "scheduling" in c.text.lower() or "process" in c.text.lower()
                   for c in doc.text_chunks)

    def test_parse_pdf_memory_management(self):
        path = find_os_doc("Memory_Management")
        if not path:
            pytest.skip("OS document not available")
        doc = self.parser.parse(path)
        assert doc.doc_type == "pdf"
        assert len(doc.text_chunks) > 0
        assert any("paging" in c.text.lower() or "virtual memory" in c.text.lower() or "tlb" in c.text.lower()
                   for c in doc.text_chunks)

    def test_parse_pdf_concurrency(self):
        path = find_os_doc("Concurrency_Synchronization")
        if not path:
            pytest.skip("OS document not available")
        doc = self.parser.parse(path)
        assert doc.doc_type == "pdf"
        assert len(doc.text_chunks) > 0

    def test_parse_pdf_file_systems(self):
        path = find_os_doc("Storage_File_Systems")
        if not path:
            pytest.skip("OS document not available")
        doc = self.parser.parse(path)
        assert doc.doc_type == "pdf"
        assert len(doc.text_chunks) > 0

    def test_parsed_document_has_metadata(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available")
        doc = self.parser.parse(path)
        assert doc.source_file
        for chunk in doc.text_chunks:
            assert chunk.source_file
            assert chunk.doc_type == "pdf"

    def test_unsupported_extension_raises(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            self.parser.parse(Path("report.csv"))


# ── Chunker tests ─────────────────────────────────────────────────────────────

class TestDocumentChunker:
    parser  = DocumentParser()
    chunker = DocumentChunker(
        chunk_size=800,
        chunk_overlap=150,
        project_metadata={
            "doc_id":  "OS-SCHED-2024-001",
            "topic":   "CPU Scheduling",
            "domain":  "CPU Scheduling & Concurrency",
            "year":    2024,
        },
    )

    def test_chunk_ids_are_deterministic(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available")
        doc     = self.parser.parse(path)
        chunks1 = self.chunker.chunk_document(doc)
        chunks2 = self.chunker.chunk_document(doc)
        ids1 = [c.chunk_id for c in chunks1]
        ids2 = [c.chunk_id for c in chunks2]
        assert ids1 == ids2

    def test_chunk_ids_are_unique(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available")
        doc    = self.parser.parse(path)
        chunks = self.chunker.chunk_document(doc)
        ids    = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), "Duplicate chunk IDs found"

    def test_project_metadata_attached(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available")
        doc    = self.parser.parse(path)
        chunks = self.chunker.chunk_document(doc)
        for chunk in chunks:
            assert chunk.metadata.get("doc_id") == "OS-SCHED-2024-001"
            assert chunk.metadata.get("domain") == "CPU Scheduling & Concurrency"

    def test_text_chunks_within_size_limit(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available")
        doc    = self.parser.parse(path)
        chunks = self.chunker.chunk_document(doc)
        text_chunks = [c for c in chunks if c.kind == "text"]
        for chunk in text_chunks:
            # Allow some overshoot from splitter edge cases
            assert len(chunk.content) <= 1200, (
                f"Chunk too large: {len(chunk.content)} chars"
            )

    def test_table_chunks_preserved(self):
        path = find_os_doc("Processes_Threads")
        if not path:
            pytest.skip("OS document not available")
        doc    = self.parser.parse(path)
        chunks = self.chunker.chunk_document(doc)
        table_chunks = [c for c in chunks if c.kind == "table"]
        assert len(table_chunks) > 0
        for tc in table_chunks:
            assert "|" in tc.content   # Markdown table format
