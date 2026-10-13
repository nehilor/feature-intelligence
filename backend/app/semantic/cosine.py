import math
from collections.abc import Sequence


def vector_norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) == 0 or len(b) == 0 or len(a) != len(b):
        raise ValueError("Vectors must be non-empty and the same length")
    norm_a = vector_norm(a)
    norm_b = vector_norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        raise ValueError("Zero-norm vectors are not comparable")
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (norm_a * norm_b)
