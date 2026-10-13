import json
import logging
import time
from typing import List, Optional

from fastapi import HTTPException, status

from app.ai.prompts.decision_brief_v1 import PROMPT_VERSION
from app.ai.providers.decision_brief_base import DecisionBriefEvidenceContext, DecisionBriefProvider
from app.ai.providers.errors import ProviderError, ProviderInvalidOutputError
from app.ai.providers.registry import ProviderRegistry, get_provider_registry
from app.core.config import Settings, get_settings
from app.domain.ai_enums import AIProcessingState, CustomerImpact, Urgency
from app.persistence.models import FeatureRequest, PriorityAssessment
from app.repositories.decision_brief_repository import DecisionBriefRepository
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.priority_assessment_repository import PriorityAssessmentRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from app.schemas.decision_brief import DecisionBriefResponse

logger = logging.getLogger("app.ai")


class DecisionBriefService:
    OPERATION = "decision_brief"

    def __init__(
        self,
        request_repo: FeatureRequestRepository,
        analysis_repo: FeatureAnalysisRepository,
        relationship_repo: RequestRelationshipRepository,
        priority_repo: PriorityAssessmentRepository,
        brief_repo: DecisionBriefRepository,
        settings: Optional[Settings] = None,
        registry: Optional[ProviderRegistry] = None,
    ) -> None:
        self._request_repo = request_repo
        self._analysis_repo = analysis_repo
        self._relationship_repo = relationship_repo
        self._priority_repo = priority_repo
        self._brief_repo = brief_repo
        self._settings = settings or get_settings()
        self._registry = registry or get_provider_registry(self._settings)

    def get_brief(self, request_id: str) -> DecisionBriefResponse:
        self._require_request(request_id)
        record = self._brief_repo.get_by_request_id(request_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="decision_brief_not_found",
            )
        return self._to_response(request_id, record)

    def generate_brief(self, request_id: str) -> DecisionBriefResponse:
        request = self._require_request(request_id)
        assessment = self._priority_repo.get_by_request_id(request_id)
        if assessment is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="priority_assessment_required",
            )

        if not self._settings.ai_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="decision_brief_unavailable",
            )

        logger.info(
            "decision_brief_started",
            extra={"feature_request_id": request_id, "prompt_version": PROMPT_VERSION},
        )
        start = time.perf_counter()
        context = self._build_context(request, assessment)
        outcome = self._run_brief_generation(context)
        latency_ms = int((time.perf_counter() - start) * 1000)

        if outcome is None:
            logger.info(
                "decision_brief_failed",
                extra={"feature_request_id": request_id, "latency_ms": latency_ms},
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="decision_brief_unavailable",
            )

        record = self._brief_repo.upsert(
            feature_request_id=request_id,
            priority_assessment_id=assessment.id,
            problem=outcome.output.problem,
            evidence_summary=outcome.output.evidence_summary,
            why_it_matters=outcome.output.why_it_matters,
            risks_and_unknowns=outcome.output.risks_and_unknowns,
            recommended_next_step=outcome.output.recommended_next_step,
            provider=outcome.provider,
            model=outcome.model,
            prompt_version=PROMPT_VERSION,
        )
        logger.info(
            "decision_brief_completed",
            extra={
                "feature_request_id": request_id,
                "provider": outcome.provider,
                "model": outcome.model,
                "prompt_version": PROMPT_VERSION,
                "latency_ms": latency_ms,
            },
        )
        return self._to_response(request_id, record)

    def _build_context(self, request: FeatureRequest, assessment: PriorityAssessment) -> DecisionBriefEvidenceContext:
        analysis = self._analysis_repo.get_by_request_id(request.id)
        impact_label = CustomerImpact.UNKNOWN.value
        urgency_label = Urgency.UNKNOWN.value
        summary = None
        underlying = None
        theme = None
        if analysis and analysis.processing_state in (
            AIProcessingState.AI_COMPLETE.value,
            AIProcessingState.AI_PARTIAL.value,
        ):
            summary = analysis.summary
            underlying = analysis.underlying_need
            theme = analysis.theme
            if analysis.customer_impact:
                impact_label = analysis.customer_impact
            if analysis.urgency:
                urgency_label = analysis.urgency

        relationship_lines: List[str] = []
        for rel in self._relationship_repo.list_for_request(request.id):
            other_id = rel.request_b_id if rel.request_a_id == request.id else rel.request_a_id
            relationship_lines.append(
                f"{rel.relationship} with request {other_id} (similarity {rel.similarity_score:.2f})"
            )

        return DecisionBriefEvidenceContext(
            feature_request_id=request.id,
            title=request.title,
            description=request.description,
            support_count=assessment.support_count,
            relationship_signal_count=assessment.relationship_signal_count,
            formula_version=assessment.formula_version,
            total_score=assessment.total_score,
            priority_level=assessment.priority_level,
            strategic_alignment=assessment.strategic_alignment,
            evidence_completeness=assessment.evidence_completeness,
            demand_score=assessment.demand_score,
            impact_score=assessment.impact_score,
            urgency_score=assessment.urgency_score,
            strategic_alignment_score=assessment.strategic_alignment_score,
            customer_impact_label=impact_label,
            urgency_label=urgency_label,
            analysis_summary=summary,
            underlying_need=underlying,
            theme=theme,
            relationship_lines=relationship_lines,
        )

    def _run_brief_generation(self, context: DecisionBriefEvidenceContext):
        primary_name = self._settings.ai_primary_provider
        fallback_name = self._settings.ai_fallback_provider
        primary = self._resolve_brief_provider(primary_name)
        fallback = self._resolve_brief_provider(fallback_name)

        if primary is None and fallback is None:
            return None

        if primary is not None:
            result = self._call_provider(primary, context)
            if result is not None:
                return result
            if fallback is not None and fallback is not primary:
                return self._call_provider(fallback, context)
            return None

        if fallback is not None:
            return self._call_provider(fallback, context)
        return None

    def _call_provider(self, provider: DecisionBriefProvider, context: DecisionBriefEvidenceContext):
        try:
            return provider.generate_brief(context)
        except ProviderInvalidOutputError:
            return None
        except ProviderError:
            return None
        except Exception:
            return None

    def _resolve_brief_provider(self, name: Optional[str]) -> Optional[DecisionBriefProvider]:
        if name == "openai":
            return self._registry.openai_decision_brief
        if name == "gemini":
            return self._registry.gemini_decision_brief
        return None

    def _require_request(self, request_id: str) -> FeatureRequest:
        request = self._request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature request not found")
        return request

    def _to_response(self, request_id: str, record) -> DecisionBriefResponse:
        risks = json.loads(record.risks_and_unknowns_json)
        return DecisionBriefResponse(
            feature_request_id=request_id,
            priority_assessment_id=record.priority_assessment_id,
            problem=record.problem,
            evidence_summary=record.evidence_summary,
            why_it_matters=record.why_it_matters,
            risks_and_unknowns=risks,
            recommended_next_step=record.recommended_next_step,
            provider=record.provider,
            model=record.model,
            prompt_version=record.prompt_version,
            created_at=record.created_at,
        )
