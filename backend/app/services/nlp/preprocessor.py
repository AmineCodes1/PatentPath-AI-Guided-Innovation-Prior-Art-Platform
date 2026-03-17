"""Text preprocessing utilities for NLP-based patent similarity scoring."""

from __future__ import annotations

import re
from functools import lru_cache

import spacy
from spacy.language import Language
from spacy.tokens import Doc

PATENT_STOPWORDS = {
    "claim",
    "wherein",
    "comprising",
    "method",
    "system",
    "apparatus",
    "device",
    "plurality",
}

ALLOWED_POS = {"NOUN", "PROPN"}


@lru_cache(maxsize=1)
def get_nlp() -> Language:
    """Load and cache spaCy pipeline for all preprocessing calls."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Fallback keeps development and tests functional when model is not downloaded.
        return spacy.blank("en")


def _sanitize_text(text: str) -> str:
    lowered = text.lower().strip()
    return re.sub(r"[^a-z0-9\s]", " ", lowered)


def _is_valid_token(token_text: str, is_stop: bool) -> bool:
    return bool(token_text and len(token_text) >= 3 and not is_stop and token_text not in PATENT_STOPWORDS)


def _token_stream(doc: Doc) -> list[str]:
    terms: list[str] = []

    for token in doc:
        lemma = token.lemma_.strip().lower() if token.lemma_ else token.text.strip().lower()
        if not _is_valid_token(lemma, token.is_stop):
            continue
        terms.append(lemma)

    if doc.has_annotation("DEP"):
        for chunk in doc.noun_chunks:
            phrase = " ".join(part.lemma_.strip().lower() for part in chunk if part.lemma_.strip())
            phrase = re.sub(r"\s+", " ", phrase).strip()
            if not _is_valid_token(phrase, False):
                continue
            terms.append(phrase)

    return terms


def preprocess_text(text: str) -> list[str]:
    """Normalize text for BM25/TF-IDF by cleaning, lemmatizing, and preserving noun compounds."""
    cleaned = _sanitize_text(text)
    if not cleaned:
        return []

    doc = get_nlp()(cleaned)
    return _token_stream(doc)


def extract_technical_terms(text: str) -> list[str]:
    """Extract top technical terms (NOUN/PROPN and compounds) deduplicated in appearance order."""
    cleaned = _sanitize_text(text)
    if not cleaned:
        return []

    doc = get_nlp()(cleaned)
    terms: list[str] = []

    for token in doc:
        lemma = token.lemma_.strip().lower() if token.lemma_ else token.text.strip().lower()
        if token.pos_ not in ALLOWED_POS:
            continue
        if not _is_valid_token(lemma, token.is_stop):
            continue
        terms.append(lemma)

    if doc.has_annotation("DEP"):
        for chunk in doc.noun_chunks:
            chunk_terms = []
            for token in chunk:
                lemma = token.lemma_.strip().lower() if token.lemma_ else token.text.strip().lower()
                if token.pos_ in ALLOWED_POS and _is_valid_token(lemma, token.is_stop):
                    chunk_terms.append(lemma)
            phrase = " ".join(chunk_terms).strip()
            if _is_valid_token(phrase, False):
                terms.append(phrase)

    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        if term in seen:
            continue
        seen.add(term)
        deduped.append(term)

    return deduped[:15]
