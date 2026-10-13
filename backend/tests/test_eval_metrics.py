from evals.metrics.classification import compute_classification_report
from evals.metrics.concept_coverage import evaluate_concept_coverage
from evals.metrics.structured_output import compute_structured_output_report


def test_perfect_relationship_metrics_are_one() -> None:
    labels = ["DUPLICATE", "RELATED", "DISTINCT"]
    y_true = ["DUPLICATE", "RELATED", "DISTINCT", "DUPLICATE"]
    y_pred = list(y_true)
    report = compute_classification_report(y_true, y_pred, labels)
    assert report.accuracy == 1.0
    assert report.macro_f1 == 1.0
    assert report.per_class["DUPLICATE"].precision == 1.0
    assert report.per_class["DUPLICATE"].recall == 1.0


def test_known_confusion_matrix_metrics() -> None:
    labels = ["DUPLICATE", "RELATED", "DISTINCT"]
    y_true = ["DUPLICATE", "DUPLICATE", "RELATED", "DISTINCT"]
    y_pred = ["DUPLICATE", "RELATED", "RELATED", "DISTINCT"]
    report = compute_classification_report(y_true, y_pred, labels)
    assert report.accuracy == 0.75
    dup = report.per_class["DUPLICATE"]
    assert dup.recall == 0.5
    assert dup.precision == 1.0


def test_zero_predicted_duplicate_no_divide_by_zero() -> None:
    labels = ["DUPLICATE", "RELATED", "DISTINCT"]
    y_true = ["DUPLICATE", "DUPLICATE"]
    y_pred = ["RELATED", "DISTINCT"]
    report = compute_classification_report(y_true, y_pred, labels, zero_division=0.0)
    dup = report.per_class["DUPLICATE"]
    assert dup.precision == 0.0
    assert dup.recall == 0.0
    assert dup.f1 == 0.0


def test_concept_coverage_recall() -> None:
    report = evaluate_concept_coverage(
        case_ids=["need-1"],
        expected_by_case=[["finance reconciliation", "excel export"]],
        predicted_by_case=[
            ["Finance reconciliation workflow", "Excel export for monthly reporting"]
        ],
        pass_threshold=0.5,
    )
    assert report.mean_recall == 1.0
    assert report.pass_rate == 1.0


def test_structured_output_success_rate() -> None:
    report = compute_structured_output_report([True, True, False])
    assert report.attempted == 3
    assert report.valid == 2
    assert abs(report.success_rate - (2 / 3)) < 1e-9
