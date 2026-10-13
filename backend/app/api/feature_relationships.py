from fastapi import APIRouter, Depends

from app.api.deps import get_semantic_relationship_service
from app.schemas.relationship import RelationshipsResponse
from app.services.semantic_relationship_service import SemanticRelationshipService

router = APIRouter(prefix="/feature-requests", tags=["feature-relationships"])


@router.post("/{request_id}/relationships/analyze", response_model=RelationshipsResponse)
def analyze_feature_relationships(
    request_id: str,
    service: SemanticRelationshipService = Depends(get_semantic_relationship_service),
) -> RelationshipsResponse:
    return service.analyze(request_id)


@router.get("/{request_id}/relationships", response_model=RelationshipsResponse)
def get_feature_relationships(
    request_id: str,
    service: SemanticRelationshipService = Depends(get_semantic_relationship_service),
) -> RelationshipsResponse:
    return service.get_relationships(request_id)
