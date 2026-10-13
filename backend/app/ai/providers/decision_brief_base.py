from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.schemas.decision_brief import DecisionBriefOutput


@dataclass
class DecisionBriefEvidenceContext:
    feature_request_id: str
    title: str
    description: str
    support_count: int
    relationship_signal_count: int
    formula_version: str
    total_score: int
    priority_level: str
    strategic_alignment: str
    evidence_completeness: str
    demand_score: int
    impact_score: int
    urgency_score: int
    strategic_alignment_score: int
    customer_impact_label: str
    urgency_label: str
    analysis_summary: Optional[str]
    underlying_need: Optional[str]
    theme: Optional[str]
    relationship_lines: List[str]


@dataclass
class DecisionBriefCallResult:
    output: DecisionBriefOutput
    provider: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class DecisionBriefProvider(Protocol):
    provider_name: str

    def generate_brief(self, context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult: ...
