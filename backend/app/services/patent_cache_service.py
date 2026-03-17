"""Patent cache management for reusing DB records and refreshing OPS metadata."""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patent_record import PatentRecord
from app.services.ops_connector import OpsConnector, ops_connector

logger = logging.getLogger(__name__)

CACHE_DURATION = timedelta(days=14)
MAX_CONCURRENT_FETCHES = 5


def _parse_date(raw_date: str | None) -> date | None:
    if not raw_date:
        return None

    text = raw_date.strip()
    if not text:
        return None

    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def _normalize_country_code(pub_ref: str) -> str:
    return pub_ref[:2].upper() if len(pub_ref) >= 2 else "EP"


def _build_espacenet_url(pub_ref: str) -> str:
    return f"https://worldwide.espacenet.com/patent/search/family/{pub_ref}"


async def get_or_create_patent(
    db: AsyncSession,
    pub_ref: str,
    ops_data: OpsConnector | dict[str, Any] | None = None,
) -> PatentRecord:
    """Return cached patent if valid, otherwise refresh from OPS and persist in DB."""
    normalized_pub_ref = pub_ref.strip().upper()
    if not normalized_pub_ref:
        raise ValueError("pub_ref must not be empty")

    existing = await db.scalar(
        select(PatentRecord).where(PatentRecord.publication_number == normalized_pub_ref)
    )

    now = datetime.now(timezone.utc)
    if existing and existing.cache_expires_at and existing.cache_expires_at > now:
        return existing

    connector: OpsConnector
    if isinstance(ops_data, OpsConnector):
        connector = ops_data
    else:
        connector = ops_connector

    if isinstance(ops_data, dict):
        biblio = dict(ops_data)
    else:
        biblio = await connector.fetch_bibliographic(normalized_pub_ref)

    abstract = await connector.fetch_abstract(normalized_pub_ref)
    claims = await connector.fetch_claims(normalized_pub_ref)
    legal_status = await connector.fetch_legal_status(normalized_pub_ref)

    publication_date = _parse_date(str(biblio.get("publication_date") or "")) or date.today()
    priority_date = _parse_date(str(biblio.get("priority_date") or ""))

    payload = {
        "publication_number": normalized_pub_ref,
        "country_code": _normalize_country_code(normalized_pub_ref),
        "title": str(biblio.get("title") or normalized_pub_ref),
        "abstract": abstract or "No abstract available.",
        "claims": claims,
        "description": None,
        "applicants": [str(item) for item in (biblio.get("applicants") or [])],
        "inventors": [str(item) for item in (biblio.get("inventors") or [])],
        "ipc_classes": [str(item) for item in (biblio.get("ipc_classes") or [])],
        "cpc_classes": [str(item) for item in (biblio.get("cpc_classes") or [])],
        "publication_date": publication_date,
        "priority_date": priority_date,
        "family_id": None,
        "legal_status": legal_status,
        "espacenet_url": _build_espacenet_url(normalized_pub_ref),
        "cached_at": now,
        "cache_expires_at": now + CACHE_DURATION,
    }

    if existing is None:
        patent = PatentRecord(**payload)
        db.add(patent)
    else:
        for key, value in payload.items():
            setattr(existing, key, value)
        patent = existing

    await db.flush()
    await db.commit()
    await db.refresh(patent)
    return patent


async def bulk_fetch_and_cache(
    db: AsyncSession,
    pub_refs: list[str],
    connector: OpsConnector | None = None,
) -> list[PatentRecord]:
    """Fetch and cache a batch of patent references with bounded concurrency."""
    unique_refs = list(dict.fromkeys(ref.strip().upper() for ref in pub_refs if ref and ref.strip()))
    if not unique_refs:
        return []

    active_connector = connector or ops_connector
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

    async def _worker(reference: str) -> PatentRecord | None:
        async with semaphore:
            try:
                return await get_or_create_patent(db=db, pub_ref=reference, ops_data=active_connector)
            except Exception as exc:  # pragma: no cover - resilience path
                logger.warning("Failed to cache patent %s: %s", reference, exc)
                return None

    results = await asyncio.gather(*(_worker(reference) for reference in unique_refs))
    return [record for record in results if record is not None]
