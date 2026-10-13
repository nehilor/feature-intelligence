from typing import Optional

from pydantic import BaseModel, Field

from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType


class RelationshipClassificationOutput(BaseModel):
    relationship: RequestRelationshipType
    confidence: RelationshipConfidence
    reason: str = Field(..., min_length=1, max_length=1000)


class RelationshipItemResponse(BaseModel):
    feature_request_id: str
    title: str
    relationship: RequestRelationshipType
    similarity_score: float
    confidence: RelationshipConfidence
    reason: str
    support_count: int = 0


class RelationshipsResponse(BaseModel):
    feature_request_id: str
    status: str = "ok"
    items: list[RelationshipItemResponse] = Field(default_factory=list)
    message: Optional[str] = None
