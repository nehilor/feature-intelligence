import pytest
from app.semantic.candidate_retrieval import retrieve_top_k_candidates
from app.semantic.cosine import cosine_similarity


def test_identical_vectors_highest_similarity() -> None:
    a = [1.0, 0.0, 0.0]
    assert cosine_similarity(a, a) == pytest.approx(1.0)


def test_orthogonal_vectors_lower_similarity() -> None:
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_zero_norm_rejected() -> None:
    with pytest.raises(ValueError):
        cosine_similarity([0.0, 0.0], [1.0, 0.0])


def test_target_excluded_from_top_k() -> None:
    candidates = retrieve_top_k_candidates(
        target_request_id="target",
        target_vector=[1.0, 0.0],
        candidates=[("target", [1.0, 0.0]), ("other", [1.0, 0.0])],
        min_score=0.0,
        top_k=5,
    )
    assert [c.feature_request_id for c in candidates] == ["other"]


def test_minimum_threshold_enforced() -> None:
    candidates = retrieve_top_k_candidates(
        target_request_id="target",
        target_vector=[1.0, 0.0],
        candidates=[("a", [0.0, 1.0])],
        min_score=0.5,
        top_k=5,
    )
    assert candidates == []


def test_top_k_enforced() -> None:
    candidates = retrieve_top_k_candidates(
        target_request_id="target",
        target_vector=[1.0, 0.0],
        candidates=[
            ("a", [1.0, 0.0]),
            ("b", [0.9, 0.1]),
            ("c", [0.8, 0.2]),
        ],
        min_score=0.0,
        top_k=2,
    )
    assert len(candidates) == 2


def test_deterministic_tie_ordering() -> None:
    candidates = retrieve_top_k_candidates(
        target_request_id="target",
        target_vector=[1.0, 0.0],
        candidates=[("b-id", [1.0, 0.0]), ("a-id", [1.0, 0.0])],
        min_score=0.0,
        top_k=5,
    )
    assert [c.feature_request_id for c in candidates] == ["a-id", "b-id"]
