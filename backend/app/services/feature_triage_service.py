import logging
import time
from typing import Optional

from fastapi import HTTPException, status

from app.ai.prompts.feature_triage_v1 import PROMPT_VERSION
from app.ai.providers.base import AIProvider
from app.ai.providers.errors import ProviderError, ProviderInvalidOutputError
from app.ai.providers.registry import ProviderRegistry, get_provider_registry
from app.core.config import Settings, get_settings
from app.domain.ai_enums import AIProcessingState
from app.persistence.models import FeatureAnalysis, FeatureRequest
from app.repositories.ai_execution_repository import AIExecutionRepository
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.schemas.triage import (
    AIMetadata,
    AnalysisContent,
    FeatureAnalysisResponse,
    TriageAnalysisOutput,
)

logger = logging.getLogger("app.ai")


class FeatureTriageService:
    OPERATION = "feature_triage"

    def __init__(
        self,
        request_repo: FeatureRequestRepository,
        analysis_repo: FeatureAnalysisRepository,
        execution_repo: AIExecutionRepository,
        settings: Optional[Settings] = None,
        registry: Optional[ProviderRegistry] = None,
    ) -> None:
        self._request_repo = request_repo
        self._analysis_repo = analysis_repo
        self._execution_repo = execution_repo
        self._settings = settings or get_settings()
        self._registry = registry or get_provider_registry(self._settings)

    def get_analysis(self, request_id: str) -> FeatureAnalysisResponse:
        request = self._require_request(request_id)
        record = self._analysis_repo.get_by_request_id(request.id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="analysis_not_found",
            )
        return self._to_response(request.id, record)

    def analyze(self, request_id: str, *, force: bool = False) -> FeatureAnalysisResponse:
        request = self._require_request(request_id)
        existing = self._analysis_repo.get_by_request_id(request.id)
        if existing and not force:
            if existing.processing_state in (
                AIProcessingState.AI_COMPLETE.value,
                AIProcessingState.AI_PARTIAL.value,
            ):
                return self._to_response(request.id, existing)

        if not self._settings.ai_enabled:
            logger.info(
                "feature_triage_manual_review_required",
                extra={"feature_request_id": request.id, "reason": "ai_disabled"},
            )
            record = self._persist_manual_review(request.id, message_reason="ai_disabled")
            return self._to_response(request.id, record, message="AI analysis is disabled.")

        title_before = request.title
        description_before = request.description

        logger.info(
            "feature_triage_started",
            extra={"feature_request_id": request.id, "prompt_version": PROMPT_VERSION},
        )
        start = time.perf_counter()
        outcome = self._run_triage(request.title, request.description)
        latency_ms = int((time.perf_counter() - start) * 1000)

        refreshed = self._request_repo.get_by_id(request.id)
        if refreshed and (refreshed.title != title_before or refreshed.description != description_before):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Feature request content changed during analysis",
            )

        if outcome is None:
            logger.info(
                "feature_triage_manual_review_required",
                extra={"feature_request_id": request.id, "latency_ms": latency_ms},
            )
            self._execution_repo.record(
                feature_request_id=request.id,
                operation=self.OPERATION,
                status=AIProcessingState.MANUAL_REVIEW_REQUIRED.value,
                prompt_version=PROMPT_VERSION,
                latency_ms=latency_ms,
            )
            record = self._persist_manual_review(request.id)
            return self._to_response(
                request.id,
                record,
                message="AI analysis is currently unavailable. Manual review is required.",
            )

        processing_state = AIProcessingState.AI_COMPLETE
        record = self._analysis_repo.upsert(
            feature_request_id=request.id,
            processing_state=processing_state,
            summary=outcome.output.summary,
            underlying_need=outcome.output.underlying_need,
            theme=outcome.output.theme.value,
            customer_impact=outcome.output.customer_impact.value,
            urgency=outcome.output.urgency.value,
            confidence=outcome.output.confidence.value,
            rationale=outcome.output.rationale,
            provider=outcome.provider,
            model=outcome.model,
            prompt_version=PROMPT_VERSION,
            used_fallback=outcome.used_fallback,
        )
        logger.info(
            "feature_triage_completed",
            extra={
                "feature_request_id": request.id,
                "provider": outcome.provider,
                "model": outcome.model,
                "prompt_version": PROMPT_VERSION,
                "latency_ms": latency_ms,
                "status": processing_state.value,
            },
        )
        self._execution_repo.record(
            feature_request_id=request.id,
            operation=self.OPERATION,
            status=processing_state.value,
            provider=outcome.provider,
            model=outcome.model,
            prompt_version=PROMPT_VERSION,
            latency_ms=latency_ms,
            input_tokens=outcome.input_tokens,
            output_tokens=outcome.output_tokens,
        )
        return self._to_response(request.id, record, used_fallback=outcome.used_fallback)

    def _run_triage(self, title: str, description: str) -> Optional["_TriageOutcome"]:
        primary = self._resolve_provider(self._settings.ai_primary_provider)
        fallback = self._resolve_provider(self._settings.ai_fallback_provider)

        if primary is None and fallback is None:
            return None

        if primary is not None:
            result = self._call_with_retry(primary, title, description, used_fallback=False)
            if result is not None:
                return result
            if fallback is not None and fallback is not primary:
                logger.info(
                    "feature_triage_fallback_started",
                    extra={"provider": getattr(fallback, "provider_name", "unknown")},
                )
                fb_result = self._call_with_retry(fallback, title, description, used_fallback=True)
                if fb_result is not None:
                    logger.info(
                        "feature_triage_fallback_completed",
                        extra={"provider": fb_result.provider},
                    )
                    return fb_result
            return None

        if fallback is not None:
            logger.info(
                "feature_triage_fallback_started",
                extra={
                    "provider": getattr(fallback, "provider_name", "unknown"),
                    "reason": "primary_unavailable",
                },
            )
            result = self._call_with_retry(fallback, title, description, used_fallback=True)
            if result is not None:
                logger.info(
                    "feature_triage_fallback_completed",
                    extra={"provider": result.provider},
                )
            return result
        return None

    def _call_with_retry(
        self,
        provider: AIProvider,
        title: str,
        description: str,
        *,
        used_fallback: bool,
    ) -> Optional["_TriageOutcome"]:
        last_error: Optional[Exception] = None
        for attempt in range(2):
            try:
                call = provider.analyze_feature_request(title, description)
                validated = TriageAnalysisOutput.model_validate(call.output.model_dump())
                return _TriageOutcome(
                    output=validated,
                    provider=call.provider,
                    model=call.model,
                    input_tokens=call.input_tokens,
                    output_tokens=call.output_tokens,
                    used_fallback=used_fallback,
                )
            except ProviderInvalidOutputError as exc:
                last_error = exc
                logger.warning(
                    "feature_triage_primary_failed",
                    extra={
                        "provider": provider.provider_name,
                        "reason": "invalid_output",
                        "attempt": attempt + 1,
                    },
                )
                continue
            except ProviderError as exc:
                last_error = exc
                logger.warning(
                    "feature_triage_primary_failed",
                    extra={
                        "provider": provider.provider_name,
                        "reason": type(exc).__name__,
                        "eligible_for_fallback": exc.eligible_for_fallback,
                    },
                )
                return None
        if last_error:
            logger.warning(
                "feature_triage_primary_failed",
                extra={"provider": provider.provider_name, "reason": "invalid_output_exhausted"},
            )
        return None

    def _resolve_provider(self, name: str) -> Optional[AIProvider]:
        if name == "openai":
            return self._registry.openai
        if name == "gemini":
            return self._registry.gemini
        return None

    def _persist_manual_review(self, request_id: str, message_reason: str = "unavailable") -> FeatureAnalysis:
        return self._analysis_repo.upsert(
            feature_request_id=request_id,
            processing_state=AIProcessingState.MANUAL_REVIEW_REQUIRED,
            summary=None,
            underlying_need=None,
            theme=None,
            customer_impact=None,
            urgency=None,
            confidence=None,
            rationale=None,
            provider=None,
            model=None,
            prompt_version=None,
            used_fallback=False,
        )

    def _require_request(self, request_id: str) -> FeatureRequest:
        request = self._request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature request not found")
        return request

    def _to_response(
        self,
        request_id: str,
        record: FeatureAnalysis,
        *,
        message: Optional[str] = None,
        used_fallback: bool = False,
    ) -> FeatureAnalysisResponse:
        state = AIProcessingState(record.processing_state)
        analysis: Optional[AnalysisContent] = None
        metadata: Optional[AIMetadata] = None

        if state in (AIProcessingState.AI_COMPLETE, AIProcessingState.AI_PARTIAL):
            if record.summary and record.theme:
                analysis = AnalysisContent.model_validate(
                    {
                        "summary": record.summary,
                        "underlying_need": record.underlying_need or "",
                        "theme": record.theme,
                        "customer_impact": record.customer_impact,
                        "urgency": record.urgency,
                        "confidence": record.confidence,
                        "rationale": record.rationale or "",
                    }
                )
            if record.provider and record.model and record.prompt_version:
                metadata = AIMetadata(
                    provider=record.provider,
                    model=record.model,
                    prompt_version=record.prompt_version,
                    used_fallback=used_fallback or record.used_fallback,
                )
        elif message is None:
            message = "Manual review is required."

        return FeatureAnalysisResponse(
            feature_request_id=request_id,
            processing_state=state,
            analysis=analysis,
            ai_metadata=metadata,
            message=message,
        )


class _TriageOutcome:
    def __init__(
        self,
        *,
        output: TriageAnalysisOutput,
        provider: str,
        model: str,
        input_tokens: Optional[int],
        output_tokens: Optional[int],
        used_fallback: bool,
    ) -> None:
        self.output = output
        self.provider = provider
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.used_fallback = used_fallback
