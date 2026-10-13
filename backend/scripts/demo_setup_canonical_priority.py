#!/usr/bin/env python3
"""
Prepare canonical 78-point priority demo evidence for an existing finance request.

Uses local deterministic demo fixtures only (provider=local_demo_fixture).
Does NOT impersonate OpenAI/Gemini provenance.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.ai_enums import (
    AIProcessingState,
    AnalysisConfidence,
    CustomerImpact,
    Theme,
    Urgency,
)
from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType
from app.persistence.database import get_engine, init_database
from app.core.config import get_settings
from app.persistence.models import FeatureRequest
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from sqlalchemy import select
from sqlalchemy.orm import Session

CANONICAL_TITLE = "Monthly finance analytics in Excel"
DEMO_PROVIDER = "local_demo_fixture"
DEMO_MODEL = "deterministic"


def _find_request(session: Session, request_id: Optional[str], title: Optional[str]) -> FeatureRequest:
    if request_id:
        row = session.get(FeatureRequest, request_id)
        if row is None:
            raise SystemExit(f"Feature request not found: {request_id}")
        return row
    lookup_title = title or CANONICAL_TITLE
    stmt = select(FeatureRequest).where(FeatureRequest.title == lookup_title)
    row = session.scalar(stmt)
    if row is None:
        raise SystemExit(
            f"No feature request titled '{lookup_title}'. Submit the canonical demo request first."
        )
    return row


def _find_by_title(session: Session, title: str) -> Optional[FeatureRequest]:
    return session.scalar(select(FeatureRequest).where(FeatureRequest.title == title))


def setup(*, request_id: Optional[str], title: Optional[str]) -> None:
    settings = get_settings()
    init_database(settings.database_url)
    engine = get_engine()

    with Session(engine) as session:
        target = _find_request(session, request_id, title)
        request_repo = FeatureRequestRepository(session)
        analysis_repo = FeatureAnalysisRepository(session)
        relationship_repo = RequestRelationshipRepository(session)

        analysis_repo.upsert(
            feature_request_id=target.id,
            processing_state=AIProcessingState.AI_COMPLETE,
            summary="Finance teams need recurring reporting exports for reconciliation outside the product.",
            underlying_need="Reconcile finance results using spreadsheet workflows outside the platform.",
            theme=Theme.REPORTING_AND_DATA.value,
            customer_impact=CustomerImpact.HIGH.value,
            urgency=Urgency.LOW.value,
            confidence=AnalysisConfidence.HIGH.value,
            rationale="Local deterministic demo fixture for canonical priority walkthrough.",
            provider=DEMO_PROVIDER,
            model=DEMO_MODEL,
            prompt_version="demo_fixture_v1",
        )

        for key in ("demo-sup-1", "demo-sup-2", "demo-sup-3", "demo-sup-4"):
            request_repo.add_support_signal(target.id, key)

        export_req = _find_by_title(session, "Export reports to CSV")
        dashboard_req = _find_by_title(session, "Download dashboard data")
        if export_req is None or dashboard_req is None:
            raise SystemExit(
                "Baseline demo requests missing. Run `make demo-reset` then submit the finance request."
            )

        relationship_repo.upsert(
            request_id_a=target.id,
            request_id_b=export_req.id,
            relationship=RequestRelationshipType.DUPLICATE.value,
            similarity_score=0.91,
            confidence=RelationshipConfidence.HIGH.value,
            reason="Local demo fixture: reporting export overlap.",
            provider=DEMO_PROVIDER,
            model=DEMO_MODEL,
            prompt_version="demo_fixture_v1",
        )
        relationship_repo.upsert(
            request_id_a=target.id,
            request_id_b=dashboard_req.id,
            relationship=RequestRelationshipType.RELATED.value,
            similarity_score=0.86,
            confidence=RelationshipConfidence.MEDIUM.value,
            reason="Local demo fixture: related reporting download need.",
            provider=DEMO_PROVIDER,
            model=DEMO_MODEL,
            prompt_version="demo_fixture_v1",
        )

    print("Canonical demo evidence applied (local_demo_fixture).")
    print("Next: set strategic alignment HIGH and POST /priority to obtain score 78.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup canonical 78-point demo evidence")
    parser.add_argument("--request-id", help="Target feature request id")
    parser.add_argument("--title", help="Target title (defaults to canonical finance title)")
    args = parser.parse_args()
    setup(request_id=args.request_id, title=args.title)


if __name__ == "__main__":
    main()
