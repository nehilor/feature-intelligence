from collections.abc import Sequence
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SemanticCandidate:
    feature_request_id: str
    similarity_score: float


def retrieve_top_k_candidates(
    *,
    target_request_id: str,
    target_vector: Sequence[float],
    candidates: List[Tuple[str, Sequence[float]]],
    min_score: float,
    top_k: int,
) -> List[SemanticCandidate]:
    from app.semantic.cosine import cosine_similarity

    scored: List[SemanticCandidate] = []
    for candidate_id, candidate_vector in candidates:
        if candidate_id == target_request_id:
            continue
        if len(candidate_vector) != len(target_vector):
            continue
        try:
            score = cosine_similarity(target_vector, candidate_vector)
        except ValueError:
            continue
        if score < min_score:
            continue
        scored.append(SemanticCandidate(feature_request_id=candidate_id, similarity_score=score))

    scored.sort(key=lambda item: (-item.similarity_score, item.feature_request_id))
    return scored[:top_k]
