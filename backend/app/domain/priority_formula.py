"""Centralized deterministic priority scoring for priority_formula_v1."""

from typing import Optional

from app.domain.ai_enums import CustomerImpact, Urgency
from app.domain.priority_enums import PriorityLevel, StrategicAlignment

FORMULA_VERSION = "priority_formula_v1"

MAX_SUPPORT_SCORE = 25
MAX_RELATIONSHIP_SCORE = 15
MAX_DEMAND_SCORE = 40
MAX_IMPACT_SCORE = 25
MAX_URGENCY_SCORE = 15
MAX_STRATEGIC_SCORE = 20
MAX_TOTAL_SCORE = 100


def calculate_support_score(support_count: int) -> int:
    return min(MAX_SUPPORT_SCORE, max(0, support_count) * 5)


def calculate_relationship_score(relationship_signal_count: int) -> int:
    return min(MAX_RELATIONSHIP_SCORE, max(0, relationship_signal_count) * 5)


def calculate_demand_score(support_count: int, relationship_signal_count: int) -> int:
    return calculate_support_score(support_count) + calculate_relationship_score(relationship_signal_count)


def map_impact_to_score(impact: Optional[CustomerImpact]) -> int:
    if impact is None:
        return 0
    mapping = {
        CustomerImpact.UNKNOWN: 0,
        CustomerImpact.LOW: 5,
        CustomerImpact.MEDIUM: 15,
        CustomerImpact.HIGH: 25,
    }
    return mapping[impact]


def map_urgency_to_score(urgency: Optional[Urgency]) -> int:
    if urgency is None:
        return 0
    mapping = {
        Urgency.UNKNOWN: 0,
        Urgency.LOW: 3,
        Urgency.MEDIUM: 8,
        Urgency.HIGH: 15,
    }
    return mapping[urgency]


def map_strategic_alignment_to_score(alignment: StrategicAlignment) -> int:
    mapping = {
        StrategicAlignment.UNKNOWN: 0,
        StrategicAlignment.LOW: 5,
        StrategicAlignment.MEDIUM: 12,
        StrategicAlignment.HIGH: 20,
    }
    return mapping[alignment]


def calculate_total_score(
    demand_score: int,
    impact_score: int,
    urgency_score: int,
    strategic_alignment_score: int,
) -> int:
    total = demand_score + impact_score + urgency_score + strategic_alignment_score
    return min(MAX_TOTAL_SCORE, max(0, total))


def priority_level_from_total(total_score: int) -> PriorityLevel:
    if total_score <= 39:
        return PriorityLevel.LOW
    if total_score <= 69:
        return PriorityLevel.MEDIUM
    return PriorityLevel.HIGH
