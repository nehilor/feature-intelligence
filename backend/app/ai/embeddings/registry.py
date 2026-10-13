from typing import Optional

from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.openai_embedding import OpenAIEmbeddingProvider
from app.core.config import Settings

_registry_override: Optional[EmbeddingProvider] = None


def set_embedding_provider(provider: Optional[EmbeddingProvider]) -> None:
    global _registry_override
    _registry_override = provider


def clear_embedding_provider() -> None:
    global _registry_override
    _registry_override = None


def get_embedding_provider(settings: Settings) -> Optional[EmbeddingProvider]:
    if _registry_override is not None:
        return _registry_override
    if not settings.openai_api_key:
        return None
    return OpenAIEmbeddingProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        timeout_seconds=float(settings.ai_request_timeout_seconds),
    )
