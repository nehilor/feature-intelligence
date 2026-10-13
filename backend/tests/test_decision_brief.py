import os

import pytest
from app.ai.providers.errors import ProviderServerError, ProviderTimeoutError
from app.ai.providers.fake_decision_brief import (
    fake_brief_failure,
    fake_brief_success,
)
from app.ai.providers.registry import ProviderRegistry, set_provider_registry
from app.core.config import get_settings
from app.domain.ai_enums import (
    AIProcessingState,
    AnalysisConfidence,
    CustomerImpact,
    Theme,
    Urgency,
)
from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType
from app.persistence.database import get_engine
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker


def _session():
    Session = sessionmaker(bind=get_engine())
    return Session()


def _create(client: TestClient) -> str:
    response = client.post(
        "/api/feature-requests",
        json={
            "title": "Export reports",
            "description": "Finance team needs reporting data in spreadsheets monthly.",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _install_brief_providers(openai_brief, gemini_brief) -> None:
    set_provider_registry(
        ProviderRegistry(
            openai=None,
            gemini=None,
            openai_decision_brief=openai_brief,
            gemini_decision_brief=gemini_brief,
        )
    )


@pytest.fixture
def ai_client(client: TestClient) -> TestClient:
    os.environ["AI_ENABLED"] = "true"
    get_settings.cache_clear()
    return client


def _seed_priority_state(client: TestClient, request_id: str) -> None:
    with _session() as db:
        FeatureAnalysisRepository(db).upsert(
            feature_request_id=request_id,
            processing_state=AIProcessingState.AI_COMPLETE,
            summary="Summary",
            underlying_need="Need export",
            theme=Theme.REPORTING_AND_DATA.value,
            customer_impact=CustomerImpact.HIGH.value,
            urgency=Urgency.LOW.value,
            confidence=AnalysisConfidence.HIGH.value,
            rationale="Rationale",
            provider="test",
            model="test",
            prompt_version="feature_triage_v1",
        )
    other = _create(client)
    with _session() as db:
        RequestRelationshipRepository(db).upsert(
            request_id_a=request_id,
            request_id_b=other,
            relationship=RequestRelationshipType.RELATED.value,
            similarity_score=0.88,
            confidence=RelationshipConfidence.HIGH.value,
            reason="Related.",
            provider="test",
            model="test",
            prompt_version="relationship_classification_v1",
        )
    client.post(f"/api/feature-requests/{request_id}/priority", json={"strategic_alignment": "HIGH"})


def test_openai_brief_success_skips_gemini(ai_client: TestClient) -> None:
    openai = fake_brief_success("openai", "fake-openai")
    gemini = fake_brief_success("gemini", "gemini-2.5-flash")
    _install_brief_providers(openai, gemini)
    request_id = _create(ai_client)
    _seed_priority_state(ai_client, request_id)

    response = ai_client.post(f"/api/feature-requests/{request_id}/decision-brief")
    assert response.status_code == 200
    body = response.json()
    assert body["prompt_version"] == "decision_brief_v1"
    assert body["provider"] == "openai"
    assert openai.call_count == 1
    assert gemini.call_count == 0

    priority = ai_client.get(f"/api/feature-requests/{request_id}/priority").json()
    assert priority["total_score"] == priority["total_score"]


def test_openai_failure_gemini_brief(ai_client: TestClient) -> None:
    openai = fake_brief_failure("openai", "fake", ProviderTimeoutError("timeout"))
    gemini = fake_brief_success("gemini", "gemini-2.5-flash")
    _install_brief_providers(openai, gemini)
    request_id = _create(ai_client)
    _seed_priority_state(ai_client, request_id)

    response = ai_client.post(f"/api/feature-requests/{request_id}/decision-brief")
    assert response.status_code == 200
    assert response.json()["provider"] == "gemini"
    assert openai.call_count >= 1
    assert gemini.call_count == 1


def test_both_providers_fail_priority_unchanged(ai_client: TestClient) -> None:
    openai = fake_brief_failure("openai", "fake", ProviderServerError("down"))
    gemini = fake_brief_failure("gemini", "fake", ProviderServerError("down"))
    _install_brief_providers(openai, gemini)
    request_id = _create(ai_client)
    _seed_priority_state(ai_client, request_id)
    before = ai_client.get(f"/api/feature-requests/{request_id}/priority").json()

    response = ai_client.post(f"/api/feature-requests/{request_id}/decision-brief")
    assert response.status_code == 503
    after = ai_client.get(f"/api/feature-requests/{request_id}/priority").json()
    assert after["total_score"] == before["total_score"]
    assert ai_client.get(f"/api/feature-requests/{request_id}/decision-brief").status_code == 404
