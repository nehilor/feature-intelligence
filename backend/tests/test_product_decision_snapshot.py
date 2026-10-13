from typing import Optional

from app.domain.ai_enums import (
    AIProcessingState,
    AnalysisConfidence,
    CustomerImpact,
    Theme,
    Urgency,
)
from app.domain.priority_formula import FORMULA_VERSION
from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType
from app.persistence.database import get_engine
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker


def _session():
    Session = sessionmaker(bind=get_engine())
    return Session()


def _create(client: TestClient, title: str = "Export reports", description: Optional[str] = None) -> str:
    desc = description or "Finance team needs reporting data in spreadsheets monthly."
    response = client.post("/api/feature-requests", json={"title": title, "description": desc})
    assert response.status_code == 201
    return response.json()["id"]


def _seed_canonical_78(client: TestClient, request_id: str) -> None:
    _seed_analysis(request_id, impact=CustomerImpact.HIGH, urgency=Urgency.LOW)
    for i in range(4):
        response = client.post(
            f"/api/feature-requests/{request_id}/support",
            json={"supporter_key": f"sup-{i}"},
        )
        assert response.status_code == 200
    other1 = _create(client, "Alpha req", "Another request for relationship signal.")
    other2 = _create(client, "Beta req", "Another request for relationship signal two.")
    _add_relationship(request_id, other1, RequestRelationshipType.DUPLICATE)
    _add_relationship(request_id, other2, RequestRelationshipType.RELATED)


def _seed_analysis(request_id: str, *, impact: CustomerImpact, urgency: Urgency) -> None:
    with _session() as db:
        FeatureAnalysisRepository(db).upsert(
            feature_request_id=request_id,
            processing_state=AIProcessingState.AI_COMPLETE,
            summary="Reporting need.",
            underlying_need="Export analytics.",
            theme=Theme.REPORTING_AND_DATA.value,
            customer_impact=impact.value,
            urgency=urgency.value,
            confidence=AnalysisConfidence.HIGH.value,
            rationale="Test seed.",
            provider="test",
            model="test",
            prompt_version="feature_triage_v1",
        )


def _add_relationship(request_id: str, other_id: str, rel: RequestRelationshipType) -> None:
    with _session() as db:
        RequestRelationshipRepository(db).upsert(
            request_id_a=request_id,
            request_id_b=other_id,
            relationship=rel.value,
            similarity_score=0.9,
            confidence=RelationshipConfidence.HIGH.value,
            reason="Test relationship.",
            provider="test",
            model="test",
            prompt_version="relationship_classification_v1",
        )


def _assert_snapshot(body: dict, *, level: str, total: int) -> None:
    snap = body["system_recommendation_at_decision"]
    assert snap["priority_level"] == level
    assert snap["total_score"] == total
    assert snap["formula_version"] == FORMULA_VERSION


def test_snapshot_on_override(client: TestClient) -> None:
    request_id = _create(client)
    _seed_canonical_78(client, request_id)
    priority = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )
    assert priority.json()["total_score"] == 78

    decision = client.post(
        f"/api/feature-requests/{request_id}/decision",
        json={
            "decision": "OVERRIDDEN",
            "reviewer_priority": "MEDIUM",
            "override_reason": "Strong demand, but current platform dependencies make immediate delivery impractical.",
        },
    )
    assert decision.status_code == 200
    body = decision.json()
    _assert_snapshot(body, level="HIGH", total=78)
    assert body["reviewer_priority"] == "MEDIUM"


def test_recalculation_does_not_rewrite_decision_snapshot(client: TestClient) -> None:
    request_id = _create(client)
    _seed_canonical_78(client, request_id)
    client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )
    client.post(
        f"/api/feature-requests/{request_id}/decision",
        json={
            "decision": "OVERRIDDEN",
            "reviewer_priority": "MEDIUM",
            "override_reason": "Strong demand, but current platform dependencies make immediate delivery impractical.",
        },
    )

    client.post(
        f"/api/feature-requests/{request_id}/support",
        json={"supporter_key": "extra-supporter"},
    )
    recalc = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )
    assert recalc.json()["total_score"] == 83

    decision = client.get(f"/api/feature-requests/{request_id}/decision")
    _assert_snapshot(decision.json(), level="HIGH", total=78)
    assert client.get(f"/api/feature-requests/{request_id}/priority").json()["total_score"] == 83


def test_client_cannot_forge_system_snapshot(client: TestClient) -> None:
    request_id = _create(client)
    _seed_canonical_78(client, request_id)
    client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )

    response = client.post(
        f"/api/feature-requests/{request_id}/decision",
        json={
            "decision": "APPROVED",
            "system_total_score": 1,
            "system_priority_level": "LOW",
            "system_formula_version": "forged",
        },
    )
    assert response.status_code == 200
    _assert_snapshot(response.json(), level="HIGH", total=78)


def test_approved_also_snapshots(client: TestClient) -> None:
    request_id = _create(client)
    _seed_canonical_78(client, request_id)
    client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )

    response = client.post(
        f"/api/feature-requests/{request_id}/decision",
        json={"decision": "APPROVED"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "APPROVED"
    _assert_snapshot(body, level="HIGH", total=78)
    snap = body["system_recommendation_at_decision"]
    assert snap["demand_score"] == 30
    assert snap["impact_score"] == 25
    assert snap["urgency_score"] == 3
    assert snap["strategic_alignment_score"] == 20
