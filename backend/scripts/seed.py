"""Deterministic demo seed for SPEC-002. Resets feature request tables and loads sample data."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings
from app.persistence.base import Base
from app.persistence.database import get_engine, init_database
from app.persistence.models import FeatureRequest, SupportSignal, utcnow
from sqlalchemy.orm import Session

SEED_REQUESTS = [
    (
        "Export reports to CSV",
        "Our operations team needs to export dashboard reporting data as CSV for analysis outside the platform.",
        ["supporter-a", "supporter-b", "supporter-c"],
    ),
    (
        "Download dashboard data",
        "Users want to download analytics data so they can work with it in spreadsheets.",
        ["supporter-a", "supporter-d"],
    ),
    (
        "Dark mode",
        "Users working late at night want a dark interface to reduce eye strain.",
        ["supporter-e"],
    ),
    (
        "Slack notifications",
        "Our team wants important product activity sent to a Slack channel.",
        [],
    ),
    (
        "Enterprise SSO",
        "Enterprise customers need to authenticate through their corporate identity provider.",
        ["supporter-f", "supporter-g", "supporter-h", "supporter-i"],
    ),
]


def seed() -> None:
    settings = get_settings()
    init_database(settings.database_url)
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        for title, description, supporters in SEED_REQUESTS:
            request = FeatureRequest(title=title, description=description, created_at=utcnow(), updated_at=utcnow())
            session.add(request)
            session.flush()
            for key in supporters:
                session.add(
                    SupportSignal(
                        feature_request_id=request.id,
                        supporter_key=key,
                        created_at=utcnow(),
                    )
                )
        session.commit()
    print(f"Seeded {len(SEED_REQUESTS)} feature requests.")


if __name__ == "__main__":
    seed()
