import importlib.util
from pathlib import Path

from app.core.config import get_settings
from app.domain.priority_formula import FORMULA_VERSION
from app.persistence.database import get_engine, init_database
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _run_demo_setup(request_id: str) -> None:
    backend = Path(__file__).resolve().parents[1]
    script = backend / "scripts" / "demo_setup_canonical_priority.py"
    spec = importlib.util.spec_from_file_location("demo_setup", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.setup(request_id=request_id, title=None)


def test_demo_setup_reaches_score_78(client: TestClient) -> None:
    for title, desc in [
        ("Export reports to CSV", "CSV export for dashboard reporting data."),
        ("Download dashboard data", "Download analytics for spreadsheets."),
    ]:
        client.post("/api/feature-requests", json={"title": title, "description": desc})

    finance = client.post(
        "/api/feature-requests",
        json={
            "title": "Monthly finance analytics in Excel",
            "description": (
                "Our finance team needs monthly analytics in Excel "
                "so they can reconcile results outside the platform."
            ),
        },
    )
    assert finance.status_code == 201
    request_id = finance.json()["id"]

    _run_demo_setup(request_id)

    priority = client.post(
        f"/api/feature-requests/{request_id}/priority",
        json={"strategic_alignment": "HIGH"},
    )
    assert priority.status_code == 200
    body = priority.json()
    assert body["total_score"] == 78
    assert body["priority_level"] == "HIGH"
    assert body["formula_version"] == FORMULA_VERSION

    settings = get_settings()
    init_database(settings.database_url)
    from app.repositories.feature_analysis_repository import FeatureAnalysisRepository

    with Session(get_engine()) as session:
        analysis = FeatureAnalysisRepository(session).get_by_request_id(request_id)
        assert analysis is not None
        assert analysis.provider == "local_demo_fixture"
