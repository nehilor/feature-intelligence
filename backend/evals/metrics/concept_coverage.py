"""Transparent concept-coverage for underlying-need evaluation."""

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class ConceptCaseResult:
    case_id: str
    expected_concepts: List[str]
    predicted_concepts: List[str]
    matched: List[str]
    recall: float
    passed: bool


@dataclass
class ConceptCoverageReport:
    case_results: List[ConceptCaseResult]
    mean_recall: float
    pass_rate: float
    pass_threshold: float


def _concept_matched(expected: str, predicted: Sequence[str]) -> bool:
    needle = expected.strip().lower()
    if not needle:
        return False
    for item in predicted:
        hay = item.strip().lower()
        if needle in hay or hay in needle:
            return True
    blob = " ".join(p.strip().lower() for p in predicted)
    return needle in blob


def evaluate_concept_coverage(
    *,
    case_ids: Sequence[str],
    expected_by_case: Sequence[List[str]],
    predicted_by_case: Sequence[List[str]],
    pass_threshold: float = 0.5,
) -> ConceptCoverageReport:
    if not (len(case_ids) == len(expected_by_case) == len(predicted_by_case)):
        raise ValueError("case input lengths must match")

    results: List[ConceptCaseResult] = []
    recalls: List[float] = []
    passes = 0
    for case_id, expected, predicted in zip(case_ids, expected_by_case, predicted_by_case):
        if not expected:
            recall = 1.0
            matched: List[str] = []
        else:
            matched = [c for c in expected if _concept_matched(c, predicted)]
            recall = len(matched) / len(expected)
        passed = recall >= pass_threshold
        if passed:
            passes += 1
        recalls.append(recall)
        results.append(
            ConceptCaseResult(
                case_id=case_id,
                expected_concepts=list(expected),
                predicted_concepts=list(predicted),
                matched=matched,
                recall=recall,
                passed=passed,
            )
        )

    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0
    pass_rate = passes / len(results) if results else 0.0
    return ConceptCoverageReport(
        case_results=results,
        mean_recall=mean_recall,
        pass_rate=pass_rate,
        pass_threshold=pass_threshold,
    )
