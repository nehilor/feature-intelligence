from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class EmbeddingResult:
    vector: List[float]
    provider: str
    model: str


class EmbeddingProvider(Protocol):
    provider_name: str
    model: str

    def embed_text(self, text: str) -> EmbeddingResult: ...
