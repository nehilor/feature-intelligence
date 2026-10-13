from dataclasses import dataclass

from app.persistence.models import PriorityAssessment


@dataclass(frozen=True)
class ProductDecisionSystemSnapshot:
    system_priority_level: str
    system_total_score: int
    system_formula_version: str
    system_demand_score: int
    system_impact_score: int
    system_urgency_score: int
    system_strategic_alignment_score: int


def snapshot_from_priority_assessment(assessment: PriorityAssessment) -> ProductDecisionSystemSnapshot:
    return ProductDecisionSystemSnapshot(
        system_priority_level=assessment.priority_level,
        system_total_score=assessment.total_score,
        system_formula_version=assessment.formula_version,
        system_demand_score=assessment.demand_score,
        system_impact_score=assessment.impact_score,
        system_urgency_score=assessment.urgency_score,
        system_strategic_alignment_score=assessment.strategic_alignment_score,
    )
