from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.persistence.database import get_db_session
from app.repositories.ai_execution_repository import AIExecutionRepository
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_embedding_repository import FeatureEmbeddingRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from app.services.embedding_service import EmbeddingService
from app.services.feature_request_service import FeatureRequestService
from app.services.feature_triage_service import FeatureTriageService
from app.services.semantic_relationship_service import SemanticRelationshipService


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


def get_semantic_relationship_service(db: Session = Depends(get_db)) -> SemanticRelationshipService:
    request_repo = FeatureRequestRepository(db)
    analysis_repo = FeatureAnalysisRepository(db)
    embedding_repo = FeatureEmbeddingRepository(db)
    embedding_service = EmbeddingService(request_repo, analysis_repo, embedding_repo)
    return SemanticRelationshipService(
        request_repo,
        embedding_repo,
        RequestRelationshipRepository(db),
        embedding_service,
        analysis_repo,
    )
