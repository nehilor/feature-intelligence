from typing import Optional

from app.domain.ai_enums import (
    AIProcessingState,
    AnalysisConfidence,
    CustomerImpact,
    Theme,
    Urgency,
)
from app.domain.priority_enums import EvidenceCompleteness
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


def _add_support(client: TestClient, request_id: str, key: str) -> None:
    response = client.post(
        f"/api/feature-requests/{request_id}/support",
        json={"supporter_key": key},
    )
    assert response.status_code == 200


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


def test_priority_not_found(client: TestClient) -> None:
    request_id = _create(client)
    response = client.get(f"/api/feature-requests/{request_id}/priority")
    assert response.status_code == 404
    assert response.json()["detail"] == "priority_not_found"


def test_canonical_priority_api(client: TestClient) -> None:
    target = _create(
        client,
        "Monthly finance analytics in Excel",
        "Our finance team needs monthly analytics in Excel so they can reconcile results outside the platform.",
    )
    other1 = _create(client, "CSV export", "Export reporting to CSV for finance.")
    other2 = _create(client, "Dashboard download", "Download dashboard data.")
    _seed_analysis(target, impact=CustomerImpact.HIGH, urgency=Urgency.LOW)
    for i in range(4):
        _add_support(client, target, f"supporter-{i}")
    _add_relationship(target, other1, RequestRelationshipType.DUPLICATE)
    _add_relationship(target, other2, RequestRelationshipType.RELATED)

    response = client.post(
        f"/api/feature-requests/{target}/priority",
        json={"strategic_alignment": "HIGH"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_score"] == 78
    assert body["priority_level"] == "HIGH"
    assert body["formula_version"] == "priority_formula_v1"
    breakdown = body["breakdown"]
    assert breakdown["demand"]["score"] == 30
    assert breakdown["demand"]["support_count"] == 4
    assert breakdown["demand"]["relationship_signal_count"] == 2
    assert breakdown["customer_impact"]["score"] == 25
    assert breakdown["urgency"]["score"] == 3
    assert breakdown["strategic_alignment"]["score"] == 20


def test_distinct_relationship_does_not_count(client: TestClient) -> None:
    target = _create(client)
    other = _create(client, "Other", "Another feature request for testing.")
    _add_relationship(target, other, RequestRelationshipType.DISTINCT)
    response = client.post(
        f"/api/feature-requests/{target}/priority",
        json={"strategic_alignment": "LOW"},
    )
    assert response.status_code == 200
    assert response.json()["breakdown"]["demand"]["relationship_signal_count"] == 0


def test_missing_analysis_partial_evidence(client: TestClient) -> None:
    request_id = _create(client)
    response = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "MEDIUM"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["evidence_completeness"] == EvidenceCompleteness.PARTIAL.value
    assert body["breakdown"]["customer_impact"]["score"] == 0


def test_recalculation_when_support_changes(client: TestClient) -> None:
    request_id = _create(client)
    first = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "UNKNOWN"},
    )
    assert first.status_code == 200
    score_before = first.json()["total_score"]
    _add_support(client, request_id, "user-a")
    second = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "UNKNOWN"},
    )
    assert second.json()["total_score"] > score_before


def test_strategic_recalculation(client: TestClient) -> None:
    request_id = _create(client)
    low = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "LOW"},
    )
    high = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )
    assert high.json()["total_score"] > low.json()["total_score"]


def test_override_does_not_mutate_priority(client: TestClient) -> None:
    request_id = _create(client)
    _seed_analysis(request_id, impact=CustomerImpact.HIGH, urgency=Urgency.LOW)
    for i in range(4):
        _add_support(client, request_id, f"s-{i}")
    other1 = _create(client, "Alpha req", "Another request for relationship signal.")
    other2 = _create(client, "Beta req", "Another request for relationship signal two.")
    _add_relationship(request_id, other1, RequestRelationshipType.DUPLICATE)
    _add_relationship(request_id, other2, RequestRelationshipType.RELATED)

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
    snap = decision.json()["system_recommendation_at_decision"]
    assert snap["priority_level"] == "HIGH"
    assert snap["total_score"] == 78
    assert decision.json()["reviewer_priority"] == "MEDIUM"

    after = client.get(f"/api/feature-requests/{request_id}/priority")
    assert after.json()["total_score"] == 78
    assert after.json()["priority_level"] == "HIGH"


def test_same_priority_override_rejected(client: TestClient) -> None:
    request_id = _create(client)
    client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "UNKNOWN"},
    )
    response = client.post(
        f"/api/feature-requests/{request_id}/decision",
        json={
            "decision": "OVERRIDDEN",
            "reviewer_priority": "LOW",
            "override_reason": "This override should fail because system is also LOW.",
        },
    )
    assert response.status_code == 422


def test_decision_requires_priority(client: TestClient) -> None:
    request_id = _create(client)
    response = client.post(
        f"/api/feature-requests/{request_id}/decision",
        json={"decision": "APPROVED"},
    )
    assert response.status_code == 409
