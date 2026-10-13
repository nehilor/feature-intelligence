import logging
from typing import Optional, Tuple

from fastapi import HTTPException, status

from app.domain.ai_enums import AIProcessingState, CustomerImpact, Urgency
from app.domain.priority_enums import EvidenceCompleteness, PriorityLevel, StrategicAlignment
from app.domain.priority_formula import (
    FORMULA_VERSION,
    calculate_demand_score,
    calculate_relationship_score,
    calculate_support_score,
    calculate_total_score,
    map_impact_to_score,
    map_strategic_alignment_to_score,
    map_urgency_to_score,
    priority_level_from_total,
)
from app.domain.relationship_enums import RequestRelationshipType
from app.persistence.models import FeatureAnalysis, PriorityAssessment
from app.repositories.feature_analysis_repository import FeatureAnalysisRepository
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.priority_assessment_repository import PriorityAssessmentRepository
from app.repositories.request_relationship_repository import RequestRelationshipRepository
from app.schemas.priority import (
    DemandBreakdown,
    PriorityAssessmentResponse,
    PriorityBreakdown,
    ScoredDimensionBreakdown,
)

logger = logging.getLogger("app.priority")


class PriorityService:
    def __init__(
        self,
        request_repo: FeatureRequestRepository,
        analysis_repo: FeatureAnalysisRepository,
        relationship_repo: RequestRelationshipRepository,
        priority_repo: PriorityAssessmentRepository,
    ) -> None:
        self._request_repo = request_repo
        self._analysis_repo = analysis_repo
        self._relationship_repo = relationship_repo
        self._priority_repo = priority_repo

    def get_priority(self, request_id: str) -> PriorityAssessmentResponse:
        self._require_request(request_id)
        record = self._priority_repo.get_by_request_id(request_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="priority_not_found",
            )
        return self._to_response(request_id, record)

    def calculate_priority(
        self, request_id: str, strategic_alignment: StrategicAlignment
    ) -> PriorityAssessmentResponse:
        self._require_request(request_id)
        existing = self._priority_repo.get_by_request_id(request_id)
        is_recalc = existing is not None

        breakdown = self._compute_breakdown(request_id, strategic_alignment)
        record = self._priority_repo.upsert(
            feature_request_id=request_id,
            support_count=breakdown["support_count"],
            relationship_signal_count=breakdown["relationship_signal_count"],
            demand_score=breakdown["demand_score"],
            impact_score=breakdown["impact_score"],
            urgency_score=breakdown["urgency_score"],
            strategic_alignment=strategic_alignment.value,
            strategic_alignment_score=breakdown["strategic_alignment_score"],
            total_score=breakdown["total_score"],
            priority_level=breakdown["priority_level"].value,
            evidence_completeness=breakdown["evidence_completeness"].value,
            formula_version=FORMULA_VERSION,
        )
        event = "priority_assessment_recalculated" if is_recalc else "priority_assessment_calculated"
        logger.info(
            event,
            extra={
                "feature_request_id": request_id,
                "formula_version": FORMULA_VERSION,
                "total_score": record.total_score,
                "priority_level": record.priority_level,
            },
        )
        return self._to_response(request_id, record)

    def _compute_breakdown(self, request_id: str, strategic_alignment: StrategicAlignment) -> dict:
        support_count = self._request_repo.count_support(request_id)
        relationship_signal_count = self._count_qualifying_relationships(request_id)
        support_score = calculate_support_score(support_count)
        relationship_score = calculate_relationship_score(relationship_signal_count)
        demand_score = calculate_demand_score(support_count, relationship_signal_count)

        impact_enum, urgency_enum = self._load_trusted_analysis_dimensions(request_id)
        impact_score = map_impact_to_score(impact_enum)
        urgency_score = map_urgency_to_score(urgency_enum)
        strategic_alignment_score = map_strategic_alignment_to_score(strategic_alignment)
        total_score = calculate_total_score(demand_score, impact_score, urgency_score, strategic_alignment_score)
        level = priority_level_from_total(total_score)
        completeness = self._evidence_completeness(request_id, strategic_alignment, impact_enum, urgency_enum)
        return {
            "support_count": support_count,
            "relationship_signal_count": relationship_signal_count,
            "support_score": support_score,
            "relationship_score": relationship_score,
            "demand_score": demand_score,
            "impact_enum": impact_enum,
            "impact_score": impact_score,
            "urgency_enum": urgency_enum,
            "urgency_score": urgency_score,
            "strategic_alignment_score": strategic_alignment_score,
            "total_score": total_score,
            "priority_level": level,
            "evidence_completeness": completeness,
        }

    def _count_qualifying_relationships(self, request_id: str) -> int:
        qualifying = {RequestRelationshipType.DUPLICATE.value, RequestRelationshipType.RELATED.value}
        rows = self._relationship_repo.list_for_request(request_id)
        return sum(1 for row in rows if row.relationship in qualifying)

    def _load_trusted_analysis_dimensions(self, request_id: str) -> Tuple[Optional[CustomerImpact], Optional[Urgency]]:
        record = self._analysis_repo.get_by_request_id(request_id)
        if record is None or not self._analysis_is_trustworthy(record):
            return None, None
        impact = CustomerImpact(record.customer_impact) if record.customer_impact else None
        urgency = Urgency(record.urgency) if record.urgency else None
        return impact, urgency

    @staticmethod
    def _analysis_is_trustworthy(record: FeatureAnalysis) -> bool:
        return record.processing_state in (
            AIProcessingState.AI_COMPLETE.value,
            AIProcessingState.AI_PARTIAL.value,
        )

    def _evidence_completeness(
        self,
        request_id: str,
        strategic_alignment: StrategicAlignment,
        impact: Optional[CustomerImpact],
        urgency: Optional[Urgency],
    ) -> EvidenceCompleteness:
        if strategic_alignment == StrategicAlignment.UNKNOWN:
            return EvidenceCompleteness.PARTIAL
        record = self._analysis_repo.get_by_request_id(request_id)
        if record is None or not self._analysis_is_trustworthy(record):
            return EvidenceCompleteness.PARTIAL
        if impact is None or urgency is None:
            return EvidenceCompleteness.PARTIAL
        return EvidenceCompleteness.COMPLETE

    def _require_request(self, request_id: str):
        request = self._request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature request not found")
        return request

    def _to_response(self, request_id: str, record: PriorityAssessment) -> PriorityAssessmentResponse:
        impact_value = CustomerImpact.UNKNOWN.value
        urgency_value = Urgency.UNKNOWN.value
        analysis = self._analysis_repo.get_by_request_id(request_id)
        if analysis and self._analysis_is_trustworthy(analysis):
            if analysis.customer_impact:
                impact_value = analysis.customer_impact
            if analysis.urgency:
                urgency_value = analysis.urgency

        strategic = StrategicAlignment(record.strategic_alignment)
        return PriorityAssessmentResponse(
            feature_request_id=request_id,
            priority_level=PriorityLevel(record.priority_level),
            total_score=record.total_score,
            formula_version=record.formula_version,
            evidence_completeness=EvidenceCompleteness(record.evidence_completeness),
            strategic_alignment=strategic,
            breakdown=PriorityBreakdown(
                demand=DemandBreakdown(
                    score=record.demand_score,
                    support_count=record.support_count,
                    relationship_signal_count=record.relationship_signal_count,
                ),
                customer_impact=ScoredDimensionBreakdown(
                    value=impact_value,
                    score=record.impact_score,
                    max_score=25,
                ),
                urgency=ScoredDimensionBreakdown(
                    value=urgency_value,
                    score=record.urgency_score,
                    max_score=15,
                ),
                strategic_alignment=ScoredDimensionBreakdown(
                    value=strategic.value,
                    score=record.strategic_alignment_score,
                    max_score=20,
                ),
            ),
        )
