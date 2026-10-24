import json
import openai
from pathlib import Path
from config.settings import get_settings

settings = get_settings()

METADATA_PROMPT = """Extract the following metadata from the first few pages of this database management systems document. Return ONLY JSON.
- doc_id: a code like DBMS-XX-YYYY-### (if present, else infer from topic and year)
- topic: the main DBMS topic covered (e.g., "B+ Trees", "Transaction Management", "Normalization", "Query Optimization")
- domain: one of [Relational Model & SQL, Normalization & Schema Design, Storage & Indexing, Transaction Management, Query Processing & Optimization, Database Recovery, Distributed Databases, NoSQL & Modern Architectures]
- year: 4-digit year of publication or last revision

Document content (first 3000 chars):
{content}
"""

_client = openai.AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base,
)


async def extract_metadata_from_document(content: str, file_path: Path) -> dict:
    """Call LLM to infer metadata from the document's first pages."""
    try:
        response = await _client.chat.completions.create(
            model=settings.openai_chat_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": METADATA_PROMPT.format(content=content[:3000])}],
        )
        meta = json.loads(response.choices[0].message.content)
        if not meta.get("doc_id"):
            meta["doc_id"] = f"DBMS-AUTO-{meta.get('year', '2024')}-001"
        if not meta.get("year"):
            meta["year"] = 2024
        if not meta.get("domain"):
            meta["domain"] = "Database Systems"
        return meta
    except Exception as e:
        print(f"Metadata extraction failed: {e}")
        return {
            "doc_id": "UNKNOWN",
            "topic": "Unknown",
            "domain": "Database Systems",
            "year": 2024,
        }
