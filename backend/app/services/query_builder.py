"""CQL query builder with spaCy keyword extraction and IPC suggestion helpers."""

from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache
from typing import Final

import spacy

from app.schemas.filters import SearchFilters

MAX_KEYWORDS: Final[int] = 8
MAX_CQL_LENGTH: Final[int] = 500

DOMAIN_TO_IPC: Final[dict[str, str]] = {
    "ai": "G06N",
    "machine learning": "G06N",
    "deep learning": "G06N",
    "robot": "B25J",
    "robotics": "B25J",
    "biotech": "C12N",
    "biology": "C12N",
    "pharma": "A61K",
    "drug": "A61K",
    "energy": "H02",
    "battery": "H02",
    "communication": "H04",
    "telecom": "H04",
    "software": "G06F",
    "computing": "G06F",
    "medical": "A61B",
    "medical device": "A61B",
    "chemistry": "C07",
    "chemical": "C07",
    "mechanical": "F16",
    "gear": "F16",
}

LAST_BUILD_METADATA: dict[str, str] = {}


@lru_cache(maxsize=1)
def _nlp() -> spacy.language.Language:
    return spacy.load("en_core_web_sm")


def _sanitize_term(term: str) -> str:
    safe = re.sub(r"[\x00-\x1f\x7f]", " ", term)
    safe = re.sub(r"[\"'`\\]", " ", safe)
    safe = re.sub(r"\s+", " ", safe).strip()
    return safe


def extract_keywords(text: str) -> list[str]:
    """Extract and rank the top keyword phrases from natural language query text."""
    query_text = (text or "").strip()
    if not query_text:
        return []

    doc = _nlp()(query_text)
    candidates: list[str] = []

    for chunk in doc.noun_chunks:
        chunk_text = _sanitize_term(chunk.text.lower())
        if len(chunk_text) >= 3:
            candidates.append(chunk_text)

    for entity in doc.ents:
        entity_text = _sanitize_term(entity.text.lower())
        if len(entity_text) >= 3:
            candidates.append(entity_text)

    for token in doc:
        token_text = _sanitize_term(token.lemma_.lower())
        if token.is_stop or token.is_punct or token.is_space:
            continue
        if len(token_text) < 3:
            continue
        if token.like_num:
            continue
        candidates.append(token_text)

    ranking = Counter(candidates)
    ordered = [term for term, _ in ranking.most_common(MAX_KEYWORDS)]
    return ordered


def suggest_ipc_classes(keywords: list[str]) -> list[str]:
    """Map extracted keywords to a curated set of IPC classes."""
    if not keywords:
        return []

    normalized_keywords = [keyword.lower().strip() for keyword in keywords if keyword.strip()]
    suggestions: list[str] = []

    for keyword in normalized_keywords:
        for domain_term, ipc_class in DOMAIN_TO_IPC.items():
            if domain_term in keyword and ipc_class not in suggestions:
                suggestions.append(ipc_class)

    return suggestions


def build_cql_query(query_text: str, filters: SearchFilters) -> str:
    """Build OPS-compatible CQL query from text and normalized filter options."""
    keywords = extract_keywords(query_text)
    core_terms = keywords[:3] if keywords else [_sanitize_term(query_text)[:40] or "innovation"]

    base_clauses = [
        f'(ti="{_sanitize_term(term)}" OR ab="{_sanitize_term(term)}")'
        for term in core_terms
        if _sanitize_term(term)
    ]
    cql_parts: list[str] = [" AND ".join(base_clauses)] if base_clauses else []

    if filters.ipc_classes:
        ipc_clauses = [f'ipc="{_sanitize_term(code).upper()}"' for code in filters.ipc_classes if code]
        if ipc_clauses:
            cql_parts.append("(" + " OR ".join(ipc_clauses) + ")")

    if filters.date_from:
        cql_parts.append(f"pd>={filters.date_from.strftime('%Y%m%d')}")
    if filters.date_to:
        cql_parts.append(f"pd<={filters.date_to.strftime('%Y%m%d')}")

    if filters.country_codes:
        countries = [f'pn="{_sanitize_term(code).upper()}"' for code in filters.country_codes if code]
        if countries:
            cql_parts.append("(" + " OR ".join(countries) + ")")

    if filters.applicant:
        cql_parts.append(f'pa="{_sanitize_term(filters.applicant)}"')

    LAST_BUILD_METADATA.clear()
    if (filters.legal_status or "").strip().lower() == "active":
        LAST_BUILD_METADATA["legal_status_note"] = "OPS legal status filtering is applied after retrieval."

    cql = " AND ".join(part for part in cql_parts if part).strip()
    cql = re.sub(r"\s+", " ", cql)

    if len(cql) > MAX_CQL_LENGTH:
        cql = cql[:MAX_CQL_LENGTH].rstrip()

    return cql


def validate_cql(cql: str) -> tuple[bool, str]:
    """Validate basic CQL syntax constraints for preview and execution safety."""
    query = (cql or "").strip()
    if not query:
        return False, "CQL query is empty."

    balance = 0
    for char in query:
        if char == "(":
            balance += 1
        elif char == ")":
            balance -= 1
            if balance < 0:
                return False, "Unbalanced parentheses in CQL query."

    if balance != 0:
        return False, "Unbalanced parentheses in CQL query."

    normalized = re.sub(r"\s+", " ", query.upper())
    if "AND AND" in normalized or "OR OR" in normalized:
        return False, "CQL query contains empty boolean operands."
    if normalized.endswith(" AND") or normalized.endswith(" OR"):
        return False, "CQL query cannot end with AND/OR."
    if normalized.startswith("AND ") or normalized.startswith("OR "):
        return False, "CQL query cannot start with AND/OR."

    return True, ""
