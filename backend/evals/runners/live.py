from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai.prompts.feature_triage_v1 import PROMPT_VERSION as TRIAGE_PROMPT_VERSION
from app.ai.prompts.relationship_classification_v1 import PROMPT_VERSION as RELATIONSHIP_PROMPT_VERSION
from app.ai.providers.errors import ProviderError, ProviderInvalidOutputError
from app.ai.providers.registry import get_provider_registry
from app.ai.providers.relationship_base import RelationshipRequestContext
from app.core.config import get_settings
from evals.metrics.classification import compute_classification_report
from evals.metrics.concept_coverage import evaluate_concept_coverage
from evals.metrics.structured_output import compute_structured_output_report
from evals.runners.offline import DATASETS, EVALS_ROOT, RELATIONSHIP_LABELS, _load_json
from evals.schemas.datasets import RelationshipDataset, ThemeDataset, UnderlyingNeedDataset

RESULTS_DIR = EVALS_ROOT / "results"


@dataclass
class LiveEvalResult:
    mode: str
    provider: str
    model: Optional[str]
    prompt_versions: Dict[str, str]
    dataset_versions: Dict[str, str]
    case_limit: Optional[int]
    relationship: Dict[str, Any]
    theme: Dict[str, Any]
    underlying_need: Dict[str, Any]
    structured_output: Dict[str, Any]
    failures: List[str]


def _resolve_eval_provider(settings) -> str:
    explicit = os.environ.get("AI_EVAL_PROVIDER")
    if explicit:
        return explicit.strip().lower()
    return settings.ai_primary_provider or "openai"


def run_live_evaluation(*, max_cases: Optional[int] = None) -> LiveEvalResult:
    settings = get_settings()
    provider_name = _resolve_eval_provider(settings)
    registry = get_provider_registry(settings)

    if provider_name == "openai":
        triage = registry.openai
        relationship = registry.openai_relationship
        model = settings.openai_model
        if triage is None or relationship is None:
            raise RuntimeError(
                "Live evaluation requires OPENAI_API_KEY and OPENAI_MODEL in the environment."
            )
    elif provider_name == "gemini":
        triage = registry.gemini
        relationship = registry.gemini_relationship
        model = settings.gemini_model
        if triage is None or relationship is None:
            raise RuntimeError(
                "Live evaluation requires GEMINI_API_KEY and GEMINI_MODEL in the environment."
            )
    else:
        raise RuntimeError(f"Unsupported AI_EVAL_PROVIDER: {provider_name}")

    relationship_ds = RelationshipDataset.model_validate(_load_json(DATASETS / "relationships.json"))
    theme_ds = ThemeDataset.model_validate(_load_json(DATASETS / "themes.json"))
    need_ds = UnderlyingNeedDataset.model_validate(_load_json(DATASETS / "underlying_needs.json"))

    limit = max_cases
    rel_cases = relationship_ds.cases[:limit] if limit else relationship_ds.cases
    theme_cases = theme_ds.cases[:limit] if limit else theme_ds.cases
    need_cases = need_ds.cases[:limit] if limit else need_ds.cases

    y_true: List[str] = []
    y_pred: List[str] = []
    rel_failures: List[str] = []
    structured_flags: List[bool] = []

    for case in rel_cases:
        target = RelationshipRequestContext(
            title=case.request_a.title,
            description=case.request_a.description,
        )
        candidate = RelationshipRequestContext(
            title=case.request_b.title,
            description=case.request_b.description,
        )
        try:
            result = relationship.classify_relationship(target, candidate)
            structured_flags.append(True)
            predicted = result.output.relationship.value
        except (ProviderInvalidOutputError, ProviderError):
            structured_flags.append(False)
            predicted = "DISTINCT"
        except Exception:
            structured_flags.append(False)
            predicted = "DISTINCT"
        y_true.append(case.expected_relationship)
        y_pred.append(predicted)
        if predicted != case.expected_relationship:
            rel_failures.append(
                f"{case.case_id}: expected {case.expected_relationship}, actual {predicted}"
            )

    rel_report = compute_classification_report(y_true, y_pred, RELATIONSHIP_LABELS)
    duplicate = rel_report.per_class["DUPLICATE"]

    theme_correct = 0
    theme_failures: List[str] = []
    predicted_concepts_by_case: Dict[str, List[str]] = {}
    for case in theme_cases:
        try:
            call = triage.analyze_feature_request(case.title, case.description)
            structured_flags.append(True)
            predicted_theme = call.output.theme.value
            predicted_concepts_by_case[case.case_id] = [call.output.underlying_need]
        except (ProviderInvalidOutputError, ProviderError):
            structured_flags.append(False)
            predicted_theme = "OTHER"
            predicted_concepts_by_case[case.case_id] = []
        except Exception:
            structured_flags.append(False)
            predicted_theme = "OTHER"
            predicted_concepts_by_case[case.case_id] = []

        if predicted_theme == case.expected_theme:
            theme_correct += 1
        else:
            theme_failures.append(
                f"{case.case_id}: expected {case.expected_theme}, actual {predicted_theme}"
            )
    theme_accuracy = theme_correct / len(theme_cases) if theme_cases else 0.0

    case_ids: List[str] = []
    expected: List[List[str]] = []
    predicted: List[List[str]] = []
    for case in need_cases:
        case_ids.append(case.case_id)
        expected.append(case.expected_concepts)
        predicted.append(predicted_concepts_by_case.get(case.case_id, []))
    need_report = evaluate_concept_coverage(
        case_ids=case_ids,
        expected_by_case=expected,
        predicted_by_case=predicted,
        pass_threshold=0.5,
    )

    structured_report = compute_structured_output_report(structured_flags)

    return LiveEvalResult(
        mode="live_provider",
        provider=provider_name,
        model=model,
        prompt_versions={
            "feature_triage": TRIAGE_PROMPT_VERSION,
            "relationship_classification": RELATIONSHIP_PROMPT_VERSION,
        },
        dataset_versions={
            "relationships": relationship_ds.dataset_version,
            "themes": theme_ds.dataset_version,
            "underlying_needs": need_ds.dataset_version,
        },
        case_limit=limit,
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
        theme={"case_count": len(theme_cases), "accuracy": theme_accuracy, "failures": theme_failures},
        underlying_need={
            "case_count": len(case_ids),
            "mean_concept_recall": need_report.mean_recall,
            "pass_rate": need_report.pass_rate,
        },
        structured_output={
            "attempted": structured_report.attempted,
            "valid": structured_report.valid,
            "success_rate": structured_report.success_rate,
        },
        failures=rel_failures + theme_failures,
    )


def format_live_report(result: LiveEvalResult) -> str:
    lines = [
        "LIVE EVALUATION",
        f"Provider: {result.provider}",
        f"Model: {result.model or 'unknown'}",
        f"Prompt versions: {result.prompt_versions}",
        f"Datasets: {result.dataset_versions}",
        f"Case limit: {result.case_limit or 'all'}",
        "",
        "Relationship metrics (live — assessment-scale benchmark, not production evidence):",
        f"  accuracy: {result.relationship['accuracy']:.3f}",
        f"  macro F1: {result.relationship['macro_f1']:.3f}",
        f"  DUPLICATE precision: {result.relationship['duplicate_precision']:.3f}",
        f"  DUPLICATE recall: {result.relationship['duplicate_recall']:.3f}",
        "",
        result.relationship["confusion_matrix"],
        "",
        f"Theme accuracy: {result.theme['accuracy']:.3f}",
        f"Underlying-need mean concept recall: {result.underlying_need['mean_concept_recall']:.3f}",
        f"Structured output success: {result.structured_output['success_rate']:.3f}",
    ]
    if result.failures:
        lines.append("")
        lines.append("Sample failures:")
        lines.extend(f"  - {item}" for item in result.failures[:10])
    return "\n".join(lines)


def write_live_report(result: LiveEvalResult) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = RESULTS_DIR / f"{stamp}-{result.provider}-live.json"
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), **asdict(result)}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
