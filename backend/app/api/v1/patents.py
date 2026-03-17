"""Patent detail API routes for PatentPath."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.patent_record import PatentRecord
from app.schemas.patent_record import PatentRecordRead
from app.services.ops_connector import ops_connector
from app.services.patent_cache_service import get_or_create_patent

router = APIRouter(prefix="/patents", tags=["patents"])


def _normalize_pub_number(publication_number: str) -> str:
	normalized = publication_number.strip().upper()
	if not normalized:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="publication_number is required")
	return normalized


@router.get("/{publication_number}")
async def get_patent_detail(
	publication_number: str,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> PatentRecordRead:
	"""Return a full patent record, refreshing from OPS when cache is stale."""
	pub_ref = _normalize_pub_number(publication_number)
	patent = await get_or_create_patent(db=db, pub_ref=pub_ref)
	return PatentRecordRead.model_validate(patent)


@router.get("/{publication_number}/claims")
async def get_patent_claims(
	publication_number: str,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str | None]:
	"""Return claims text, fetching from OPS on demand if absent in DB cache."""
	pub_ref = _normalize_pub_number(publication_number)
	patent = await get_or_create_patent(db=db, pub_ref=pub_ref)

	if not patent.claims:
		patent.claims = await ops_connector.fetch_claims(pub_ref)
		await db.commit()
		await db.refresh(patent)

	return {"publication_number": pub_ref, "claims": patent.claims}


@router.get("/{publication_number}/family")
async def get_patent_family(
	publication_number: str,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
	"""Return INPADOC family members with basic bibliographic metadata."""
	pub_ref = _normalize_pub_number(publication_number)
	family_refs = await ops_connector.fetch_family(pub_ref)

	members: list[dict[str, object]] = []
	for family_ref in family_refs:
		try:
			biblio = await ops_connector.fetch_bibliographic(family_ref)
		except Exception:
			biblio = {}

		members.append(
			{
				"publication_number": family_ref,
				"title": biblio.get("title"),
				"publication_date": biblio.get("publication_date"),
			}
		)

	existing = await db.scalar(select(PatentRecord).where(PatentRecord.publication_number == pub_ref))
	if existing is not None and members:
		existing.family_id = members[0]["publication_number"]
		await db.commit()

	return {"publication_number": pub_ref, "family_members": members}


@router.get("/{publication_number}/legal")
async def get_patent_legal_status(
	publication_number: str,
	db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
	"""Return legal status for a publication, honoring OPS 24h Redis caching."""
	pub_ref = _normalize_pub_number(publication_number)
	patent = await db.scalar(select(PatentRecord).where(PatentRecord.publication_number == pub_ref))

	legal_status = await ops_connector.fetch_legal_status(pub_ref)
	if patent is not None:
		patent.legal_status = legal_status
		patent.cached_at = datetime.now(timezone.utc)
		await db.commit()

	return {"publication_number": pub_ref, "legal_status": legal_status}
