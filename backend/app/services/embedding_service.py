import logging
from typing import List, Optional, Tuple

from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.openai_embedding import EmbeddingProviderError
from app.ai.embeddings.registry import get_embedding_provider
from app.core.config import Settings, get_settings
from app.domain.ai_enums import AIProcessingState
from app.persistence.models import FeatureRequest
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_embedding_repository import FeatureEmbeddingRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.semantic.embedding_text import build_canonical_embedding_text, compute_embedding_content_hash
from app.semantic.vector_validation import deserialize_embedding, serialize_embedding, validate_embedding_vector

logger = logging.getLogger("app.ai")


class EmbeddingUnavailableError(Exception):
    pass


class EmbeddingService:
    def __init__(
        self,
        request_repo: FeatureRequestRepository,
        analysis_repo: FeatureAnalysisRepository,
        embedding_repo: FeatureEmbeddingRepository,
        settings: Optional[Settings] = None,
        provider: Optional[EmbeddingProvider] = None,
    ) -> None:
        self._request_repo = request_repo
        self._analysis_repo = analysis_repo
        self._embedding_repo = embedding_repo
        self._settings = settings or get_settings()
        self._provider = provider if provider is not None else get_embedding_provider(self._settings)

    def get_or_create_vector(self, feature_request_id: str) -> Tuple[List[float], str, str]:
        request = self._request_repo.get_by_id(feature_request_id)
        if request is None:
            raise ValueError("Feature request not found")
        canonical = self._canonical_for_request(request)
        if self._provider is None:
            raise EmbeddingUnavailableError("Embedding provider is not configured")
        content_hash = compute_embedding_content_hash(
            self._provider.provider_name,
            self._provider.model,
            canonical,
        )
        existing = self._embedding_repo.get_by_request_id(feature_request_id)
        if (
            existing is not None
            and existing.content_hash == content_hash
            and existing.provider == self._provider.provider_name
            and existing.model == self._provider.model
        ):
            logger.info(
                "embedding_reused",
                extra={"feature_request_id": feature_request_id, "embedding_model": existing.model},
            )
            return deserialize_embedding(existing.embedding), existing.provider, existing.model

        logger.info(
            "embedding_generation_started",
            extra={"feature_request_id": feature_request_id, "embedding_model": self._provider.model},
        )
        try:
            result = self._provider.embed_text(canonical)
        except EmbeddingProviderError as exc:
            logger.warning(
                "embedding_generation_failed",
                extra={"feature_request_id": feature_request_id, "reason": str(exc)},
            )
            raise EmbeddingUnavailableError(str(exc)) from exc

        vector = validate_embedding_vector(result.vector)
        self._embedding_repo.upsert(
            feature_request_id=feature_request_id,
            embedding_json=serialize_embedding(vector),
            provider=result.provider,
            model=result.model,
            content_hash=content_hash,
        )
        logger.info(
            "embedding_generated",
            extra={"feature_request_id": feature_request_id, "embedding_model": result.model},
        )
        return vector, result.provider, result.model

    def _canonical_for_request(self, request: FeatureRequest) -> str:
        underlying_need: Optional[str] = None
        analysis = self._analysis_repo.get_by_request_id(request.id)
        if analysis is not None and analysis.processing_state in (
            AIProcessingState.AI_COMPLETE.value,
            AIProcessingState.AI_PARTIAL.value,
        ):
            if analysis.underlying_need and analysis.underlying_need.strip():
                underlying_need = analysis.underlying_need
        return build_canonical_embedding_text(request.title, request.description, underlying_need)
