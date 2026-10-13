from typing import Optional

from pydantic import BaseModel

from app.domain.priority_enums import (
    EvidenceCompleteness,
    PriorityLevel,
    StrategicAlignment,
)


class PriorityCalculateRequest(BaseModel):
    strategic_alignment: StrategicAlignment


class DemandBreakdown(BaseModel):
    score: int
    max_score: int = 40
    support_count: int
    relationship_signal_count: int


class ScoredDimensionBreakdown(BaseModel):
    value: str
    score: int
    max_score: int


class PriorityBreakdown(BaseModel):
    demand: DemandBreakdown
    customer_impact: ScoredDimensionBreakdown
    urgency: ScoredDimensionBreakdown
    strategic_alignment: ScoredDimensionBreakdown


class PriorityAssessmentResponse(BaseModel):
    feature_request_id: str
    priority_level: PriorityLevel
    total_score: int
    formula_version: str
    evidence_completeness: EvidenceCompleteness
    breakdown: PriorityBreakdown
    strategic_alignment: StrategicAlignment
    message: Optional[str] = None
