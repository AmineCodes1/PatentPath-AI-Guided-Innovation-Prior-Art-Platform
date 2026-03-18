"""IPC classification API endpoints for browse and fuzzy search flows."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, TypedDict

from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/classifications", tags=["classifications"])


class IPCClass(TypedDict):
    """Typed representation of one IPC class entry from JSON data."""

    code: str
    title: str
    description: str
    keywords: list[str]


class IPCSection(TypedDict):
    """Typed representation of one IPC top-level section."""

    section: str
    title: str
    classes: list[IPCClass]


class IPCPayload(TypedDict):
    """Typed representation of the JSON payload root."""

    sections: list[IPCSection]


@lru_cache(maxsize=1)
def _load_ipc_data() -> IPCPayload:
    """Load and cache curated IPC section/class definitions from disk."""
    data_path = Path(__file__).resolve().parents[2] / "data" / "ipc_classes.json"
    with data_path.open("r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)

    sections = payload.get("sections")
    if not isinstance(sections, list):
        raise RuntimeError("Invalid IPC data format: missing sections list")

    return payload


def _flatten_classes(payload: IPCPayload) -> list[IPCClass]:
    """Flatten nested sections into a single list of classes for search and lookup."""
    classes: list[IPCClass] = []
    for section in payload["sections"]:
        classes.extend(section["classes"])
    return classes


def _score_ipc_match(entry: IPCClass, normalized_query: str) -> int:
    """Compute simple fuzzy score from code/title/description/keywords overlap."""
    query_terms = [term for term in normalized_query.split() if term]
    if not query_terms:
        return 0

    score = 0
    code = entry["code"].lower()
    title = entry["title"].lower()
    description = entry["description"].lower()
    keywords = [item.lower() for item in entry.get("keywords", [])]

    for term in query_terms:
        if term in code:
            score += 8
        if term in title:
            score += 5
        if term in description:
            score += 3
        if any(term in keyword for keyword in keywords):
            score += 4

    return score


@router.get("/ipc")
def get_ipc_tree() -> IPCPayload:
    """Return the full curated IPC classification tree."""
    return _load_ipc_data()


@router.get("/ipc/search")
def search_ipc_classes(
    q: Annotated[str, Query(min_length=1, description="Free-text query for IPC title/keywords/code")],
) -> list[IPCClass]:
    """Return top 5 fuzzy matches against IPC class title, description, and keywords."""
    normalized_query = q.strip().lower()
    if not normalized_query:
        return []

    payload = _load_ipc_data()
    scored_matches: list[tuple[int, IPCClass]] = []

    for entry in _flatten_classes(payload):
        score = _score_ipc_match(entry, normalized_query)
        if score > 0:
            scored_matches.append((score, entry))

    scored_matches.sort(key=lambda item: (-item[0], item[1]["code"]))
    return [entry for _, entry in scored_matches[:5]]


@router.get("/ipc/{code}")
def get_ipc_class(code: str) -> IPCClass:
    """Return one IPC class entry by code, raising 404 when not found."""
    target = code.strip().upper()
    payload = _load_ipc_data()

    for entry in _flatten_classes(payload):
        if entry["code"].upper() == target:
            return entry

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"IPC class {target} not found",
    )
