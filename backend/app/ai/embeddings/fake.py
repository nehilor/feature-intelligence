import hashlib
import math
from typing import Callable, List, Optional

from app.ai.embeddings.base import EmbeddingResult


def deterministic_vector(text: str, dimensions: int = 16) -> List[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    raw = [((digest[i % len(digest)] / 255.0) * 2.0 - 1.0) for i in range(dimensions)]
    norm = math.sqrt(sum(v * v for v in raw))
    if norm == 0.0:
        raw[0] = 1.0
        norm = 1.0
    return [v / norm for v in raw]


class FakeEmbeddingProvider:
    provider_name = "openai"
    model = "fake-embedding-model"

    def __init__(
        self,
        vector_fn: Optional[Callable[[str], List[float]]] = None,
        *,
        provider_name: str = "openai",
        model: str = "fake-embedding-model",
    ) -> None:
        self.provider_name = provider_name
        self.model = model
        self._vector_fn = vector_fn or deterministic_vector
        self.call_count = 0

    def embed_text(self, text: str) -> EmbeddingResult:
        self.call_count += 1
        vector = self._vector_fn(text)
        return EmbeddingResult(vector=vector, provider=self.provider_name, model=self.model)
