from app.domain.ai_enums import CustomerImpact, Urgency
from app.domain.priority_enums import PriorityLevel, StrategicAlignment
from app.domain.priority_formula import (
    calculate_demand_score,
    calculate_relationship_score,
    calculate_support_score,
    calculate_total_score,
    map_impact_to_score,
    map_strategic_alignment_to_score,
    map_urgency_to_score,
    priority_level_from_total,
)


def test_empty_evidence_scores_zero_and_low() -> None:
    demand = calculate_demand_score(0, 0)
    impact = map_impact_to_score(None)
    urgency = map_urgency_to_score(None)
    strategic = map_strategic_alignment_to_score(StrategicAlignment.UNKNOWN)
    total = calculate_total_score(demand, impact, urgency, strategic)
    assert total == 0
    assert priority_level_from_total(total) == PriorityLevel.LOW


def test_canonical_78_point_scenario() -> None:
    support_score = calculate_support_score(4)
    relationship_score = calculate_relationship_score(2)
    assert support_score == 20
    assert relationship_score == 10
    demand = calculate_demand_score(4, 2)
    assert demand == 30
    impact = map_impact_to_score(CustomerImpact.HIGH)
    urgency = map_urgency_to_score(Urgency.LOW)
    strategic = map_strategic_alignment_to_score(StrategicAlignment.HIGH)
    assert impact == 25
    assert urgency == 3
    assert strategic == 20
    total = calculate_total_score(demand, impact, urgency, strategic)
    assert total == 78
    assert priority_level_from_total(total) == PriorityLevel.HIGH


def test_support_score_caps_at_25() -> None:
    assert calculate_support_score(100) == 25


def test_relationship_score_caps_at_15() -> None:
    assert calculate_relationship_score(100) == 15


def test_total_never_exceeds_100() -> None:
    demand = calculate_demand_score(100, 100)
    impact = map_impact_to_score(CustomerImpact.HIGH)
    urgency = map_urgency_to_score(Urgency.HIGH)
    strategic = map_strategic_alignment_to_score(StrategicAlignment.HIGH)
    total = calculate_total_score(demand, impact, urgency, strategic)
    assert total <= 100


def test_priority_level_boundaries() -> None:
    assert priority_level_from_total(0) == PriorityLevel.LOW
    assert priority_level_from_total(39) == PriorityLevel.LOW
    assert priority_level_from_total(40) == PriorityLevel.MEDIUM
    assert priority_level_from_total(69) == PriorityLevel.MEDIUM
    assert priority_level_from_total(70) == PriorityLevel.HIGH
    assert priority_level_from_total(100) == PriorityLevel.HIGH
