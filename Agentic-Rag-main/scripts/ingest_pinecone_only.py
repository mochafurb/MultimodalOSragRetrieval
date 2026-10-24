"""
scripts/ingest_pinecone_only.py
────────────────────────────────
Simplified ingestion script that:
  1. Parses + chunks each PDF from the data/ directory
  2. Embeds chunks via OpenRouter (text-embedding-3-large)
  3. Upserts vectors + metadata into Pinecone
  
No PostgreSQL required. Full chunk content is stored in Pinecone metadata
(content_preview up to 1000 chars) so the agent can work without a DB.
"""

import asyncio
import sys
import io
from pathlib import Path

# Force UTF-8 output on Windows to avoid emoji encoding errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).parent.parent))

from pinecone import Pinecone, ServerlessSpec
from ingestion.parser import DocumentParser
from ingestion.chunker import DocumentChunker
from ingestion.embedder import Embedder
from config.settings import get_settings

settings = get_settings()

BATCH_SIZE = 50  # vectors per upsert


async def main():
    print("=" * 60)
    print("DBMS RAG — Pinecone-Only Ingestion")
    print("=" * 60)

    # ── Pinecone setup ────────────────────────────────────────────
    print(f"\n🔌 Connecting to Pinecone index: {settings.pinecone_index_name}")
    pc = Pinecone(api_key=settings.pinecone_api_key)
    existing = [i.name for i in pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        print(f"   Creating new index '{settings.pinecone_index_name}' (dim=1536, cosine)…")
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Wait for index to be ready
        import time
        for _ in range(30):
            idx_info = pc.describe_index(settings.pinecone_index_name)
            if idx_info.status.ready:
                break
            print("   ⏳ Waiting for index to be ready…")
            time.sleep(5)
    else:
        print(f"   ✅ Index already exists")

    index = pc.Index(settings.pinecone_index_name)

    # Clean previous vectors in namespace so OS vectors are pristine
    try:
        print(f"   🧹 Clearing old vectors in namespace '{settings.pinecone_namespace_text}'…")
        index.delete(delete_all=True, namespace=settings.pinecone_namespace_text)
        print("   ✅ Namespace cleared")
    except Exception as e:
        print(f"   ⚠️  Could not clear namespace: {e}")

    # ── Find data files ───────────────────────────────────────────
    data_dir = Path(__file__).parent.parent / "data"
    pdf_files = sorted(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {data_dir}")
        return

    print(f"\n📚 Found {len(pdf_files)} PDF file(s) in {data_dir}")

    # ── Process each file ─────────────────────────────────────────
    parser = DocumentParser()
    embedder = Embedder()
    total_indexed = 0
    total_failed = 0

    for pdf_path in pdf_files:
        print(f"\n📄 Processing: {pdf_path.name}")
        try:
            # Parse
            parsed = parser.parse(pdf_path)
            print(f"   ✔ Parsed: {len(parsed.text_chunks)} text elements")

            # Chunk
            chunker = DocumentChunker(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
            chunks = chunker.chunk_document(parsed)
            text_chunks = [c for c in chunks if c.kind == "text"]
            print(f"   ✔ Chunked: {len(text_chunks)} text chunks")

            if not text_chunks:
                print(f"   ⚠️  No text chunks produced, skipping")
                continue

            # Embed in small batches to avoid timeouts
            print(f"   ⏳ Embedding {len(text_chunks)} chunks…")
            embedded_chunks = await embedder.embed_chunks(text_chunks)
            print(f"   ✔ Embedded {len(embedded_chunks)} chunks")

            # Build Pinecone vectors
            vectors = []
            for ec in embedded_chunks:
                chunk = ec.chunk
                meta = {
                    "chunk_id":        chunk.chunk_id,
                    "kind":            chunk.kind,
                    "source_file":     chunk.metadata.get("source_file", pdf_path.name),
                    "doc_type":        chunk.metadata.get("doc_type", "pdf"),
                    "doc_id":          chunk.metadata.get("doc_id", ""),
                    "topic":           chunk.metadata.get("topic", ""),
                    "domain":          chunk.metadata.get("domain", "Operating Systems"),
                    "year":            chunk.metadata.get("year", 2024),
                    "page_or_slide":   chunk.metadata.get("page_or_slide", 0),
                    "section_title":   chunk.metadata.get("section_title", ""),
                    # Store up to 1000 chars so agent can answer without DB
                    "content_preview": chunk.content[:1000],
                }
                vectors.append({
                    "id": chunk.chunk_id,
                    "values": ec.embedding,
                    "metadata": meta,
                })

            # Upsert to Pinecone in batches
            ns = settings.pinecone_namespace_text
            for i in range(0, len(vectors), BATCH_SIZE):
                batch = vectors[i : i + BATCH_SIZE]
                index.upsert(vectors=batch, namespace=ns)
                print(f"   ✔ Upserted batch {i//BATCH_SIZE + 1} ({len(batch)} vectors)")

            total_indexed += len(vectors)
            print(f"   ✅ {pdf_path.name}: {len(vectors)} vectors indexed")

        except Exception as exc:
            total_failed += 1
            print(f"   ❌ Failed: {exc}")
            import traceback
            traceback.print_exc()

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"  ✅ Total vectors indexed : {total_indexed}")
    print(f"  ❌ Files failed          : {total_failed}")

    # Show index stats
    try:
        stats = index.describe_index_stats()
        ns_text = stats.namespaces.get(settings.pinecone_namespace_text)
        count = ns_text.vector_count if ns_text else 0
        print(f"  📊 Pinecone '{settings.pinecone_namespace_text}' total: {count} vectors")
    except Exception as e:
        print(f"  ⚠️  Could not fetch index stats: {e}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
