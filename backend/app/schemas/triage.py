from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.ai_enums import (
    AIProcessingState,
    AnalysisConfidence,
    CustomerImpact,
    Theme,
    Urgency,
)


class TriageAnalysisOutput(BaseModel):
    summary: str = Field(..., min_length=1, max_length=500)
    underlying_need: str = Field(..., min_length=1, max_length=1000)
    theme: Theme
    customer_impact: CustomerImpact
    urgency: Urgency
    confidence: AnalysisConfidence
    rationale: str = Field(..., min_length=1, max_length=1000)


class AnalysisContent(BaseModel):
    summary: str
    underlying_need: str
    theme: Theme
    customer_impact: CustomerImpact
    urgency: Urgency
    confidence: AnalysisConfidence
    rationale: str


class AIMetadata(BaseModel):
    provider: str
    model: str
    prompt_version: str
    used_fallback: bool = False


class FeatureAnalysisResponse(BaseModel):
    feature_request_id: str
    processing_state: AIProcessingState
    analysis: Optional[AnalysisContent] = None
    ai_metadata: Optional[AIMetadata] = None
    message: Optional[str] = None


class FeatureAnalysisRecord(BaseModel):
    id: str
    feature_request_id: str
    processing_state: AIProcessingState
    summary: Optional[str] = None
    underlying_need: Optional[str] = None
    theme: Optional[Theme] = None
    customer_impact: Optional[CustomerImpact] = None
    urgency: Optional[Urgency] = None
    confidence: Optional[AnalysisConfidence] = None
    rationale: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
