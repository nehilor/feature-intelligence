from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.persistence.database import get_db_session
from app.repositories.ai_execution_repository import AIExecutionRepository
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.services.feature_request_service import FeatureRequestService
from app.services.feature_triage_service import FeatureTriageService


def get_db() -> Generator[Session, None, None]:
    yield from get_db_session()


def get_feature_request_service(db: Session = Depends(get_db)) -> FeatureRequestService:
    return FeatureRequestService(FeatureRequestRepository(db))


def get_feature_triage_service(db: Session = Depends(get_db)) -> FeatureTriageService:
    return FeatureTriageService(
        FeatureRequestRepository(db),
        FeatureAnalysisRepository(db),
        AIExecutionRepository(db),
    )
