from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DecisionBriefOutput(BaseModel):
    problem: str = Field(..., min_length=1, max_length=2000)
    evidence_summary: str = Field(..., min_length=1, max_length=2000)
    why_it_matters: str = Field(..., min_length=1, max_length=2000)
    risks_and_unknowns: List[str] = Field(..., min_length=1, max_length=10)
    recommended_next_step: str = Field(..., min_length=1, max_length=2000)


class DecisionBriefResponse(BaseModel):
    feature_request_id: str
    priority_assessment_id: str
    problem: str
    evidence_summary: str
    why_it_matters: str
    risks_and_unknowns: List[str]
    recommended_next_step: str
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    created_at: Optional[datetime] = None
    message: Optional[str] = None
