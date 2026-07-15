"""TF-IDF retrieval over curated legal knowledge base."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.project_paths import DATA_DIR

_KB_PATH = DATA_DIR / "legal_kb.json"

_legal_kb: List[dict] = []
_vectorizer: Optional[TfidfVectorizer] = None
_kb_vectors = None


def _kb_text(entry: dict) -> str:
    keywords = " ".join(entry.get("keywords", []))
    docs = " ".join(entry.get("documents_needed", []))
    return (
        f"{entry.get('act_name', '')} {entry.get('section', '')} "
        f"{entry.get('plain_summary', '')} {entry.get('applicable_to', '')} "
        f"{keywords} {docs}"
    )


def load_knowledge_base(kb_path: Optional[str] = None) -> List[dict]:
    """Load legal_kb.json and build TF-IDF index."""
    global _legal_kb, _vectorizer, _kb_vectors

    path = Path(kb_path) if kb_path else _KB_PATH
    with open(path, encoding="utf-8") as f:
        _legal_kb = json.load(f)

    texts = [_kb_text(e) for e in _legal_kb]
    _vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    _kb_vectors = _vectorizer.fit_transform(texts)
    return _legal_kb


def retrieve_relevant_laws(extracted_info: dict, top_k: int = 5) -> List[dict]:
    """Return top-k legal clauses matching extracted notice info."""
    if not _legal_kb or _vectorizer is None or _kb_vectors is None:
        load_knowledge_base()

    doc_type = extracted_info.get("document_type", "")
    summary = extracted_info.get("summary_one_line", "")
    sections = " ".join(extracted_info.get("legal_sections_cited", []))
    demands = " ".join(extracted_info.get("key_demands", []))
    query = f"{doc_type} {summary} {sections} {demands}"

    query_vec = _vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, _kb_vectors)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0.01:
            entry = dict(_legal_kb[idx])
            entry["relevance_score"] = float(similarities[idx])
            results.append(entry)
    return results


def format_clauses_for_prompt(clauses: List[dict]) -> str:
    """Format retrieved clauses for injection into Gemma prompt."""
    if not clauses:
        return "No specific clauses retrieved. Advise user to consult a lawyer."
    lines = []
    for c in clauses:
        lines.append(
            f"- [{c['id']}] {c['act_name']}, {c['section']}: {c['plain_summary']}\n"
            f"  Authority: {c.get('authority_to_approach', 'N/A')} | "
            f"Typical deadline: {c.get('typical_deadline_days', 'N/A')} days"
        )
    return "\n".join(lines)
