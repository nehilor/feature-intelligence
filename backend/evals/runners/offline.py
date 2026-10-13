from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from evals.metrics.classification import compute_classification_report
from evals.metrics.concept_coverage import evaluate_concept_coverage
from evals.metrics.structured_output import compute_structured_output_report
from evals.schemas.datasets import (
    EvalBaselines,
    RelationshipDataset,
    RelationshipPredictionFixture,
    StructuredOutputFixture,
    ThemeDataset,
    ThemePredictionFixture,
    UnderlyingNeedDataset,
    UnderlyingNeedPredictionFixture,
)

EVALS_ROOT = Path(__file__).resolve().parents[1]
DATASETS = EVALS_ROOT / "datasets"
FIXTURES = EVALS_ROOT / "fixtures"
RELATIONSHIP_LABELS = ["DUPLICATE", "RELATED", "DISTINCT"]


@dataclass
class OfflineEvalResult:
    mode: str
    dataset_versions: Dict[str, str]
    fixture_versions: Dict[str, str]
    relationship: Dict[str, Any]
    theme: Dict[str, Any]
    underlying_need: Dict[str, Any]
    structured_output: Dict[str, Any]
    failures: List[str]
    passed: bool


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_offline_evaluation(*, baselines_path: Optional[Path] = None) -> OfflineEvalResult:
    baselines_path = baselines_path or FIXTURES / "baselines.json"
    failures: List[str] = []

    relationship_ds = RelationshipDataset.model_validate(_load_json(DATASETS / "relationships.json"))
    theme_ds = ThemeDataset.model_validate(_load_json(DATASETS / "themes.json"))
    need_ds = UnderlyingNeedDataset.model_validate(_load_json(DATASETS / "underlying_needs.json"))

    rel_pred = RelationshipPredictionFixture.model_validate(
        _load_json(FIXTURES / "relationship_predictions.json")
    )
    theme_pred = ThemePredictionFixture.model_validate(_load_json(FIXTURES / "theme_predictions.json"))
    need_pred = UnderlyingNeedPredictionFixture.model_validate(
        _load_json(FIXTURES / "underlying_need_predictions.json")
    )
    structured_cases = StructuredOutputFixture.model_validate(
        _load_json(FIXTURES / "structured_output_cases.json")
    )
    baselines = EvalBaselines.model_validate(_load_json(baselines_path))

    rel_by_id = {item.case_id: item for item in rel_pred.predictions}
    y_true: List[str] = []
    y_pred: List[str] = []
    rel_failures: List[str] = []
    for case in relationship_ds.cases:
        pred = rel_by_id.get(case.case_id)
        if pred is None:
            failures.append(f"missing relationship prediction for {case.case_id}")
            continue
        y_true.append(case.expected_relationship)
        y_pred.append(pred.predicted_relationship)
        if pred.predicted_relationship != case.expected_relationship:
            rel_failures.append(
                f"{case.case_id}: expected {case.expected_relationship}, actual {pred.predicted_relationship}"
            )

    rel_report = compute_classification_report(y_true, y_pred, RELATIONSHIP_LABELS)
    duplicate = rel_report.per_class["DUPLICATE"]

    theme_by_id = {item.case_id: item for item in theme_pred.predictions}
    theme_correct = 0
    theme_total = 0
    theme_failures: List[str] = []
    for case in theme_ds.cases:
        pred = theme_by_id.get(case.case_id)
        if pred is None:
            failures.append(f"missing theme prediction for {case.case_id}")
            continue
        theme_total += 1
        if pred.predicted_theme == case.expected_theme:
            theme_correct += 1
        else:
            theme_failures.append(
                f"{case.case_id}: expected {case.expected_theme}, actual {pred.predicted_theme}"
            )
    theme_accuracy = theme_correct / theme_total if theme_total else 0.0

    need_by_id = {item.case_id: item for item in need_pred.predictions}
    case_ids: List[str] = []
    expected: List[List[str]] = []
    predicted: List[List[str]] = []
    for case in need_ds.cases:
        pred = need_by_id.get(case.case_id)
        if pred is None:
            failures.append(f"missing underlying-need prediction for {case.case_id}")
            continue
        case_ids.append(case.case_id)
        expected.append(case.expected_concepts)
        predicted.append(pred.predicted_concepts)
    need_report = evaluate_concept_coverage(
        case_ids=case_ids,
        expected_by_case=expected,
        predicted_by_case=predicted,
        pass_threshold=0.5,
    )

    structured_flags: List[bool] = []
    structured_flags.extend(item.structured_output_valid for item in rel_pred.predictions)
    structured_flags.extend(item.structured_output_valid for item in theme_pred.predictions)
    structured_flags.extend(item.structured_output_valid for item in need_pred.predictions)
    structured_flags.extend(item.structured_output_valid for item in structured_cases.cases)
    structured_report = compute_structured_output_report(structured_flags)

    if rel_report.macro_f1 < baselines.relationship_macro_f1_min:
        failures.append(
            f"relationship macro F1 {rel_report.macro_f1:.3f} below baseline {baselines.relationship_macro_f1_min}"
        )
    if duplicate.precision < baselines.relationship_duplicate_precision_min:
        failures.append(
            "relationship DUPLICATE precision "
            f"{duplicate.precision:.3f} below baseline {baselines.relationship_duplicate_precision_min}"
        )
    if duplicate.recall < baselines.relationship_duplicate_recall_min:
        failures.append(
            "relationship DUPLICATE recall "
            f"{duplicate.recall:.3f} below baseline {baselines.relationship_duplicate_recall_min}"
        )
    if theme_accuracy < baselines.theme_accuracy_min:
        failures.append(
            f"theme accuracy {theme_accuracy:.3f} below baseline {baselines.theme_accuracy_min}"
        )
    if need_report.mean_recall < baselines.underlying_need_mean_recall_min:
        failures.append(
            "underlying-need mean recall "
            f"{need_report.mean_recall:.3f} below baseline {baselines.underlying_need_mean_recall_min}"
        )
    if structured_report.success_rate < baselines.structured_output_success_rate_min:
        failures.append(
            "structured-output success rate "
            f"{structured_report.success_rate:.3f} below baseline {baselines.structured_output_success_rate_min}"
        )

    passed = len(failures) == 0

    return OfflineEvalResult(
        mode="offline_frozen_predictions",
        dataset_versions={
            "relationships": relationship_ds.dataset_version,
            "themes": theme_ds.dataset_version,
            "underlying_needs": need_ds.dataset_version,
        },
        fixture_versions={
            "relationship_predictions": rel_pred.fixture_version,
            "theme_predictions": theme_pred.fixture_version,
            "underlying_need_predictions": need_pred.fixture_version,
            "structured_output_cases": structured_cases.fixture_version,
            "baselines": baselines.baseline_version,
        },
        relationship={
            "case_count": len(y_true),
            "accuracy": rel_report.accuracy,
            "macro_f1": rel_report.macro_f1,
            "duplicate_precision": duplicate.precision,
            "duplicate_recall": duplicate.recall,
            "per_class": {label: asdict(metrics) for label, metrics in rel_report.per_class.items()},
            "confusion_matrix": rel_report.format_confusion_matrix(),
            "failures": rel_failures,
        },
        theme={
            "case_count": theme_total,
            "accuracy": theme_accuracy,
            "failures": theme_failures,
        },
        underlying_need={
            "case_count": len(case_ids),
            "mean_concept_recall": need_report.mean_recall,
            "pass_rate": need_report.pass_rate,
            "pass_threshold": need_report.pass_threshold,
            "failures": [r.case_id for r in need_report.case_results if not r.passed],
        },
        structured_output={
            "attempted": structured_report.attempted,
            "valid": structured_report.valid,
            "success_rate": structured_report.success_rate,
        },
        failures=failures,
        passed=passed,
    )


def format_offline_report(result: OfflineEvalResult) -> str:
    lines = [
        "OFFLINE EVALUATION",
        "Evaluation mode: offline frozen predictions",
        "No provider calls",
        "",
        f"Datasets: {result.dataset_versions}",
        f"Fixtures: {result.fixture_versions}",
        "",
        "Relationship metrics (frozen-fixture regression — not live model quality):",
        f"  cases: {result.relationship['case_count']}",
        f"  accuracy: {result.relationship['accuracy']:.3f}",
        f"  macro F1: {result.relationship['macro_f1']:.3f}",
        f"  DUPLICATE precision: {result.relationship['duplicate_precision']:.3f}",
        f"  DUPLICATE recall: {result.relationship['duplicate_recall']:.3f}",
        "",
        result.relationship["confusion_matrix"],
        "",
        "Theme metrics (frozen fixtures):",
        f"  accuracy: {result.theme['accuracy']:.3f}",
        "",
        "Underlying-need concept coverage (frozen fixtures):",
        f"  mean concept recall: {result.underlying_need['mean_concept_recall']:.3f}",
        f"  case pass rate (threshold {result.underlying_need['pass_threshold']}): "
        f"{result.underlying_need['pass_rate']:.3f}",
        "",
        "Structured output reliability (frozen fixtures):",
        f"  success rate: {result.structured_output['success_rate']:.3f} "
        f"({result.structured_output['valid']}/{result.structured_output['attempted']})",
        "",
    ]
    if result.relationship["failures"]:
        lines.append("Relationship misclassifications:")
        lines.extend(f"  - {item}" for item in result.relationship["failures"])
        lines.append("")
    if result.failures:
        lines.append("REGRESSION GATE FAILURES:")
        lines.extend(f"  - {item}" for item in result.failures)
    else:
        lines.append("Offline evaluation passed regression gates.")
    return "\n".join(lines)


def write_optional_json_report(result: OfflineEvalResult, path: Path) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **asdict(result),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
