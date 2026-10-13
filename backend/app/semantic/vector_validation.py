import json
import math
from typing import Any, List


class InvalidEmbeddingError(ValueError):
    pass


def validate_embedding_vector(values: Any) -> List[float]:
    if values is None:
        raise InvalidEmbeddingError("Embedding is missing")
    if not isinstance(values, list):
        raise InvalidEmbeddingError("Embedding must be a list of numbers")
    if not values:
        raise InvalidEmbeddingError("Embedding must be non-empty")
    vector: List[float] = []
    for item in values:
        if not isinstance(item, (int, float)):
            raise InvalidEmbeddingError("Embedding must contain only numbers")
        number = float(item)
        if not math.isfinite(number):
            raise InvalidEmbeddingError("Embedding must contain finite values")
        vector.append(number)
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        raise InvalidEmbeddingError("Embedding must have non-zero norm")
    return vector


def serialize_embedding(vector: List[float]) -> str:
    return json.dumps(vector)


def deserialize_embedding(raw: str) -> List[float]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvalidEmbeddingError("Embedding JSON is invalid") from exc
    return validate_embedding_vector(payload)
