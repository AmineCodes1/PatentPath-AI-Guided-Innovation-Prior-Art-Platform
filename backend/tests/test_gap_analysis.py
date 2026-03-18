"""Unit tests for gap analysis generation with mocked Anthropic responses."""

from __future__ import annotations

import asyncio
import math
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from app.services.gap_analysis_service import run_gap_analysis


def test_run_gap_analysis_parses_and_persists_mocked_response(monkeypatch) -> None:
    session_id = uuid4()
    patent = SimpleNamespace(
        publication_number="US1234567A1",
        title="Navigation controller",
        abstract="Autonomous navigation with sensor fusion",
        claims="A method for autonomous route planning",
    )

    fake_session = SimpleNamespace(id=session_id, query_text="autonomous vehicle navigation system")
    fake_scored_row = SimpleNamespace(patent=patent)

    db = AsyncMock()
    db.scalar = AsyncMock(side_effect=[None, fake_session])
    db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: [fake_scored_row]))

    captured = {}

    def _capture_add(instance) -> None:
        captured["analysis"] = instance

    db.add = _capture_add
    db.commit = AsyncMock()

    def _refresh(instance) -> None:
        setattr(instance, "id", uuid4())

    db.refresh = AsyncMock(side_effect=_refresh)

    class _FakeMessages:
        async def create(self, **_kwargs):
            await asyncio.sleep(0)
            payload = (
                '{"overall_risk":"MEDIUM","covered_aspects":["sensor fusion"],'
                '"gap_aspects":["edge-case fallback"],"suggestions":["add redundancy"],'
                '"narrative":"Detailed analysis","feasibility":{"technical_readiness":4,'
                '"domain_specificity":3,"claim_potential":5,"commentary":"Strong potential"}}'
            )
            return SimpleNamespace(content=[SimpleNamespace(text=payload)])

    class _FakeAnthropic:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.messages = _FakeMessages()

    monkeypatch.setattr("app.services.gap_analysis_service.anthropic.AsyncAnthropic", _FakeAnthropic)

    analysis = asyncio.run(run_gap_analysis(db, str(session_id)))

    assert analysis.session_id == session_id
    assert analysis.overall_risk.value == "MEDIUM"
    assert analysis.covered_aspects == ["sensor fusion"]
    assert analysis.gap_aspects == ["edge-case fallback"]
    assert analysis.suggestions == ["add redundancy"]

    feasibility_composite = ((analysis.feasibility_technical + analysis.feasibility_domain + analysis.feasibility_claim) / 3) * 20
    assert math.isclose(feasibility_composite, 80.0, abs_tol=1e-9)
    assert "analysis" in captured
