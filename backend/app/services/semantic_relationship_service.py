import logging
import time
from typing import List, Optional, Tuple

from fastapi import HTTPException, status

from app.ai.prompts.relationship_classification_v1 import PROMPT_VERSION
from app.ai.providers.errors import ProviderError, ProviderInvalidOutputError
from app.ai.providers.registry import ProviderRegistry, get_provider_registry
from app.ai.providers.relationship_base import RelationshipCallResult, RelationshipRequestContext
from app.core.config import Settings, get_settings
from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType
from app.persistence.models import FeatureRequest
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_embedding_repository import FeatureEmbeddingRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from app.schemas.relationship import RelationshipItemResponse, RelationshipsResponse
from app.semantic.candidate_retrieval import SemanticCandidate, retrieve_top_k_candidates
from app.semantic.vector_validation import deserialize_embedding
from app.services.embedding_service import EmbeddingService, EmbeddingUnavailableError

logger = logging.getLogger("app.ai")


class SemanticRelationshipService:
    def __init__(
        self,
        request_repo: FeatureRequestRepository,
        embedding_repo: FeatureEmbeddingRepository,
        relationship_repo: RequestRelationshipRepository,
        embedding_service: EmbeddingService,
        analysis_repo: FeatureAnalysisRepository,
        settings: Optional[Settings] = None,
        registry: Optional[ProviderRegistry] = None,
    ) -> None:
        self._request_repo = request_repo
        self._embedding_repo = embedding_repo
        self._relationship_repo = relationship_repo
        self._embedding_service = embedding_service
        self._analysis_repo = analysis_repo
        self._settings = settings or get_settings()
        self._registry = registry or get_provider_registry(self._settings)

    def get_relationships(self, request_id: str) -> RelationshipsResponse:
        self._require_request(request_id)
        return self._build_response(request_id)

    def analyze(self, request_id: str) -> RelationshipsResponse:
        target = self._require_request(request_id)
        try:
            target_vector, _, target_model = self._embedding_service.get_or_create_vector(target.id)
        except EmbeddingUnavailableError:
            return RelationshipsResponse(
                feature_request_id=target.id,
                status="embedding_unavailable",
                items=[],
                message="Relationship analysis is unavailable because embedding generation failed.",
            )

        candidates = self._retrieve_candidates(target.id, target_vector, target_model)
        logger.info(
            "semantic_candidates_retrieved",
            extra={
                "feature_request_id": target.id,
                "candidate_count": len(candidates),
                "embedding_model": target_model,
            },
        )

        if not candidates:
            return RelationshipsResponse(
                feature_request_id=target.id,
                status="ok",
                items=[],
                message="No meaningful related requests found.",
            )

        target_ctx = self._context_for_request(target)
        partial = False
        for candidate in candidates:
            other = self._request_repo.get_by_id(candidate.feature_request_id)
            if other is None:
                continue
            result = self._classify_with_failover(target_ctx, self._context_for_request(other))
            if result is None:
                partial = True
                logger.warning(
                    "relationship_classification_failed",
                    extra={
                        "feature_request_id": target.id,
                        "candidate_request_id": candidate.feature_request_id,
                    },
                )
                continue
            self._relationship_repo.upsert(
                request_id_a=target.id,
                request_id_b=other.id,
                relationship=result.output.relationship.value,
                similarity_score=candidate.similarity_score,
                confidence=result.output.confidence.value,
                reason=result.output.reason,
                provider=result.provider,
                model=result.model,
                prompt_version=PROMPT_VERSION,
            )

        response = self._build_response(target.id)
        if partial and response.items:
            response.status = "partial"
            response.message = "Some candidate relationships could not be classified."
        elif partial:
            response.status = "classification_unavailable"
            response.message = "Relationship classification is currently unavailable."
        return response

    def _retrieve_candidates(
        self,
        target_id: str,
        target_vector: List[float],
        target_model: str,
    ) -> List[SemanticCandidate]:
        candidate_vectors: List[Tuple[str, List[float]]] = []
        for request in self._request_repo.list_all():
            if request.id == target_id:
                continue
            vector = self._vector_for_request(request.id, target_model)
            if vector is None:
                continue
            candidate_vectors.append((request.id, vector))

        return retrieve_top_k_candidates(
            target_request_id=target_id,
            target_vector=target_vector,
            candidates=candidate_vectors,
            min_score=self._settings.semantic_min_candidate_score,
            top_k=self._settings.semantic_top_k,
        )

    def _vector_for_request(self, request_id: str, expected_model: str) -> Optional[List[float]]:
        record = self._embedding_repo.get_by_request_id(request_id)
        if record is not None and record.model == expected_model:
            try:
                return deserialize_embedding(record.embedding)
            except Exception:
                return None
        try:
            vector, _, model = self._embedding_service.get_or_create_vector(request_id)
        except EmbeddingUnavailableError:
            return None
        if model != expected_model:
            return None
        return vector

    def _classify_with_failover(
        self,
        target: RelationshipRequestContext,
        candidate: RelationshipRequestContext,
    ) -> Optional[RelationshipCallResult]:
        primary = self._resolve_relationship_provider(self._settings.ai_primary_provider)
        fallback = self._resolve_relationship_provider(self._settings.ai_fallback_provider)

        if primary is not None:
            result = self._call_relationship_with_retry(primary, target, candidate)
            if result is not None:
                return result
            if fallback is not None and fallback is not primary:
                logger.info("relationship_classification_started", extra={"provider": fallback.provider_name})
                return self._call_relationship_with_retry(fallback, target, candidate, used_fallback=True)
            return None

        if fallback is not None:
            logger.info(
                "relationship_classification_started",
                extra={"provider": fallback.provider_name, "reason": "primary_unavailable"},
            )
            return self._call_relationship_with_retry(fallback, target, candidate, used_fallback=True)
        return None

    def _call_relationship_with_retry(
        self,
        provider,
        target: RelationshipRequestContext,
        candidate: RelationshipRequestContext,
        *,
        used_fallback: bool = False,
    ) -> Optional[RelationshipCallResult]:
        del used_fallback
        start = time.perf_counter()
        for attempt in range(2):
            try:
                result = provider.classify_relationship(target, candidate)
                latency_ms = int((time.perf_counter() - start) * 1000)
                logger.info(
                    "relationship_classification_completed",
                    extra={
                        "provider": result.provider,
                        "model": result.model,
                        "prompt_version": PROMPT_VERSION,
                        "latency_ms": latency_ms,
                        "status": result.output.relationship.value,
                    },
                )
                return result
            except ProviderInvalidOutputError:
                continue
            except ProviderError:
                return None
        return None

    def _resolve_relationship_provider(self, name: str):
        if name == "openai":
            return self._registry.openai_relationship
        if name == "gemini":
            return self._registry.gemini_relationship
        return None

    def _context_for_request(self, request: FeatureRequest) -> RelationshipRequestContext:
        underlying_need = None
        analysis = self._analysis_repo.get_by_request_id(request.id)
        if analysis is not None and analysis.underlying_need:
            underlying_need = analysis.underlying_need
        return RelationshipRequestContext(
            title=request.title,
            description=request.description,
            underlying_need=underlying_need,
        )

    def _build_response(self, request_id: str) -> RelationshipsResponse:
        rows = self._relationship_repo.list_for_request(request_id)
        items: List[RelationshipItemResponse] = []
        for row in rows:
            other_id = row.request_b_id if row.request_a_id == request_id else row.request_a_id
            other = self._request_repo.get_by_id(other_id)
            if other is None:
                continue
            items.append(
                RelationshipItemResponse(
                    feature_request_id=other.id,
                    title=other.title,
                    relationship=RequestRelationshipType(row.relationship),
                    similarity_score=row.similarity_score,
                    confidence=RelationshipConfidence(row.confidence),
                    reason=row.reason,
                    support_count=self._request_repo.count_support(other.id),
                )
            )
        items.sort(key=lambda item: (-item.similarity_score, item.title.lower()))
        return RelationshipsResponse(feature_request_id=request_id, status="ok", items=items)

    def _require_request(self, request_id: str) -> FeatureRequest:
        request = self._request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature request not found")
        return request
