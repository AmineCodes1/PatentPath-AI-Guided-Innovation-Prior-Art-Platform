"""Integration-like tests for composite NLP scoring pipeline behavior."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.models.patent_record import PatentRecord
from app.models.scored_result import RiskLabel
from app.services.nlp.scoring_pipeline import ScoringPipeline


def _patent(publication_number: str, title: str, abstract: str, claims: str) -> PatentRecord:
    now = datetime.now(timezone.utc)
    return PatentRecord(
        publication_number=publication_number,
        country_code=publication_number[:2],
        title=title,
        abstract=abstract,
        claims=claims,
        description=None,
        applicants=["PatentPath Labs"],
        inventors=["Inventor A"],
        ipc_classes=["G06F"],
        cpc_classes=["G06F"],
        publication_date=date(2024, 1, 1),
        priority_date=None,
        family_id=None,
        legal_status="Active",
        espacenet_url=f"https://example.com/{publication_number}",
        cached_at=now,
        cache_expires_at=now + timedelta(days=7),
    )


def test_scoring_pipeline_scores_and_ranks_expected_results() -> None:
    patents = [
        _patent(
            "US1000001A1",
            "Autonomous vehicle navigation system",
            "Lidar and camera fusion for self-driving navigation with obstacle prediction.",
            "A vehicle navigation system using lidar mapping and path planning for autonomous driving.",
        ),
        _patent(
            "US1000002A1",
            "Battery management in electric buses",
            "Thermal balancing for large-scale electric bus packs.",
            "Battery thermal control and balancing circuitry.",
        ),
        _patent(
            "US1000003A1",
            "Bioreactor nutrient monitoring",
            "Sensors for fermentation nutrient concentration control.",
            "Methods to control nutrient feed in biological reactors.",
        ),
        _patent(
            "US1000004A1",
            "Drone crop spraying planner",
            "Route optimization for agricultural spraying drones.",
            "A route planning approach for spraying patterns in crop fields.",
        ),
        _patent(
            "US1000005A1",
            "Mechanical hose connector",
            "Coupling geometry for fluid hose locking.",
            "A hose coupling with quick lock features.",
        ),
    ]

    results = ScoringPipeline().score_patents("autonomous vehicle navigation system", patents)

    assert len(results) == 5
    assert all(0.0 <= item.composite_score <= 1.0 for item in results)

    assert results[0].patent_id == patents[0].id
    assert results[0].rank == 1

    for item in results:
        score = item.composite_score
        if score >= 0.80:
            assert item.risk_label == RiskLabel.HIGH
        elif score >= 0.55:
            assert item.risk_label == RiskLabel.MEDIUM
        elif score >= 0.30:
            assert item.risk_label == RiskLabel.LOW
        else:
            assert item.risk_label == RiskLabel.MINIMAL
