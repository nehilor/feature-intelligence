"""
Optional live OpenAI feature triage smoke test (not part of make verify).

Requires OPENAI_API_KEY and OPENAI_MODEL in the environment. Never prints secrets.
"""

from __future__ import annotations

import os
import sys

from app.ai.providers.registry import ProviderRegistry, set_provider_registry
from app.core.config import get_settings
from app.persistence.database import init_database, reset_database
from app.repositories.ai_execution_repository import AIExecutionRepository
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.services.feature_triage_service import FeatureTriageService


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("OPENAI_MODEL"):
        print("SKIP: OPENAI_API_KEY and OPENAI_MODEL required for live smoke test.")
        return 0

    os.environ.setdefault("AI_ENABLED", "true")
    get_settings.cache_clear()
    settings = get_settings()
    reset_database()
    init_database(settings.database_url)

    from app.ai.providers.registry import build_provider_registry

    registry = build_provider_registry(settings)
    set_provider_registry(registry)

    from sqlalchemy.orm import sessionmaker

    from app.persistence.database import get_engine

    session = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)()
    try:
        request_repo = FeatureRequestRepository(session)
        created = request_repo.create(
            title="Export reports to CSV",
            description=(
                "Our finance team spends several hours every month copying reporting data "
                "into spreadsheets for reconciliation."
            ),
        )
        service = FeatureTriageService(
            request_repo,
            FeatureAnalysisRepository(session),
            AIExecutionRepository(session),
            settings=settings,
            registry=registry,
        )
        result = service.analyze(created.id)
        print(f"processing_state={result.processing_state.value}")
        if result.analysis:
            print(f"theme={result.analysis.theme.value}")
            print(f"urgency={result.analysis.urgency.value}")
        return 0 if result.processing_state.value in {"AI_COMPLETE", "AI_PARTIAL"} else 1
    finally:
        session.close()
        reset_database()


if __name__ == "__main__":
    sys.exit(main())
