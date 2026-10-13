"""Deterministic classification metrics without external ML dependencies."""

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence


@dataclass
class PerClassMetrics:
    precision: float
    recall: float
    f1: float
    support: int


@dataclass
class ClassificationReport:
    labels: List[str]
    accuracy: float
    per_class: Dict[str, PerClassMetrics]
    macro_f1: float
    confusion: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def format_confusion_matrix(self) -> str:
        lines = ["Confusion matrix (rows=expected, cols=predicted):"]
        header = ["expected \\ pred"] + self.labels
        lines.append("\t".join(header))
        for expected in self.labels:
            row = [expected]
            for predicted in self.labels:
                row.append(str(self.confusion.get(expected, {}).get(predicted, 0)))
            lines.append("\t".join(row))
        return "\n".join(lines)


def _safe_div(numerator: float, denominator: float, zero_division: float = 0.0) -> float:
    if denominator == 0:
        return zero_division
    return numerator / denominator


def compute_classification_report(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Iterable[str],
    *,
    zero_division: float = 0.0,
) -> ClassificationReport:
    label_list = list(labels)
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")

    confusion: Dict[str, Dict[str, int]] = {label: {other: 0 for other in label_list} for label in label_list}
    correct = 0
    for truth, pred in zip(y_true, y_pred):
        if truth not in confusion:
            confusion[truth] = {other: 0 for other in label_list}
        if pred not in confusion[truth]:
            confusion[truth][pred] = 0
        confusion[truth][pred] += 1
        if truth == pred:
            correct += 1

    per_class: Dict[str, PerClassMetrics] = {}
    f1_scores: List[float] = []
    for label in label_list:
        tp = confusion.get(label, {}).get(label, 0)
        fp = sum(confusion.get(other, {}).get(label, 0) for other in label_list if other != label)
        fn = sum(confusion.get(label, {}).get(other, 0) for other in label_list if other != label)
        support = sum(confusion.get(label, {}).values())
        precision = _safe_div(tp, tp + fp, zero_division)
        recall = _safe_div(tp, tp + fn, zero_division)
        f1 = _safe_div(2 * precision * recall, precision + recall, zero_division)
        per_class[label] = PerClassMetrics(precision=precision, recall=recall, f1=f1, support=support)
        f1_scores.append(f1)

    accuracy = _safe_div(correct, len(y_true), zero_division) if y_true else zero_division
    macro_f1 = _safe_div(sum(f1_scores), len(f1_scores), zero_division) if f1_scores else zero_division

    return ClassificationReport(
        labels=label_list,
        accuracy=accuracy,
        per_class=per_class,
        macro_f1=macro_f1,
        confusion=confusion,
    )
