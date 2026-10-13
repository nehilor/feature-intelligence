from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from app.domain.priority_enums import (
    PriorityLevel,
    ProductDecisionType,
    ReviewerPriority,
)


class ProductDecisionCreate(BaseModel):
    decision: ProductDecisionType
    reviewer_priority: Optional[ReviewerPriority] = None
    override_reason: Optional[str] = None
    reviewer_note: Optional[str] = None

    @field_validator("override_reason", "reviewer_note")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_decision_fields(self) -> "ProductDecisionCreate":
        if self.decision == ProductDecisionType.OVERRIDDEN:
            if self.reviewer_priority is None:
                raise ValueError("reviewer_priority is required when decision is OVERRIDDEN")
            if not self.override_reason or len(self.override_reason.strip()) < 10:
                raise ValueError("override_reason must be at least 10 characters for OVERRIDDEN")
            if len(self.override_reason) > 2000:
                raise ValueError("override_reason is too long")
        return self


class SystemRecommendationSnapshot(BaseModel):
    priority_level: PriorityLevel
    total_score: int
    formula_version: str
    demand_score: int
    impact_score: int
    urgency_score: int
    strategic_alignment_score: int


class ProductDecisionResponse(BaseModel):
    feature_request_id: str
    priority_assessment_id: str
    decision: ProductDecisionType
    reviewer_priority: Optional[ReviewerPriority] = None
    override_reason: Optional[str] = None
    reviewer_note: Optional[str] = None
    system_recommendation_at_decision: SystemRecommendationSnapshot
    created_at: datetime
    updated_at: datetime
    message: Optional[str] = None
