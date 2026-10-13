import logging

from fastapi import HTTPException, status

from app.domain.priority_enums import PriorityLevel, ProductDecisionType, ReviewerPriority
from app.domain.product_decision_snapshot import snapshot_from_priority_assessment
from app.persistence.models import ProductDecision
from app.repositories.feature_request_repository import FeatureRequestRepository
from app.repositories.priority_assessment_repository import PriorityAssessmentRepository
from app.repositories.product_decision_repository import ProductDecisionRepository
from app.schemas.product_decision import (
    ProductDecisionCreate,
    ProductDecisionResponse,
    SystemRecommendationSnapshot,
)

logger = logging.getLogger("app.decision")


class ProductDecisionService:
    def __init__(
        self,
        request_repo: FeatureRequestRepository,
        priority_repo: PriorityAssessmentRepository,
        decision_repo: ProductDecisionRepository,
    ) -> None:
        self._request_repo = request_repo
        self._priority_repo = priority_repo
        self._decision_repo = decision_repo

    def get_decision(self, request_id: str) -> ProductDecisionResponse:
        self._require_request(request_id)
        record = self._decision_repo.get_by_request_id(request_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="decision_not_found",
            )
        return self._to_response(request_id, record)

    def create_decision(self, request_id: str, payload: ProductDecisionCreate) -> ProductDecisionResponse:
        self._require_request(request_id)
        assessment = self._priority_repo.get_by_request_id(request_id)
        if assessment is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="priority_assessment_required",
            )

        if payload.decision == ProductDecisionType.OVERRIDDEN:
            system_level = PriorityLevel(assessment.priority_level)
            if payload.reviewer_priority == ReviewerPriority(system_level.value):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="override_priority_must_differ_from_system",
                )

        snapshot = snapshot_from_priority_assessment(assessment)
        record = self._decision_repo.upsert(
            feature_request_id=request_id,
            priority_assessment_id=assessment.id,
            decision=payload.decision.value,
            reviewer_priority=(payload.reviewer_priority.value if payload.reviewer_priority else None),
            override_reason=payload.override_reason,
            reviewer_note=payload.reviewer_note,
            system_priority_level=snapshot.system_priority_level,
            system_total_score=snapshot.system_total_score,
            system_formula_version=snapshot.system_formula_version,
            system_demand_score=snapshot.system_demand_score,
            system_impact_score=snapshot.system_impact_score,
            system_urgency_score=snapshot.system_urgency_score,
            system_strategic_alignment_score=snapshot.system_strategic_alignment_score,
        )

        event = {
            ProductDecisionType.APPROVED: "product_decision_created",
            ProductDecisionType.OVERRIDDEN: "product_decision_overridden",
            ProductDecisionType.DEFERRED: "product_decision_deferred",
            ProductDecisionType.REJECTED: "product_decision_rejected",
        }[payload.decision]
        logger.info(
            event,
            extra={
                "feature_request_id": request_id,
                "decision": payload.decision.value,
                "total_score": snapshot.system_total_score,
                "priority_level": snapshot.system_priority_level,
            },
        )
        return self._to_response(request_id, record)

    def _require_request(self, request_id: str):
        request = self._request_repo.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature request not found")
        return request

    def _to_response(self, request_id: str, record: ProductDecision) -> ProductDecisionResponse:
        return ProductDecisionResponse(
            feature_request_id=request_id,
            priority_assessment_id=record.priority_assessment_id,
            decision=ProductDecisionType(record.decision),
            reviewer_priority=(
                ReviewerPriority(record.reviewer_priority) if record.reviewer_priority else None
            ),
            override_reason=record.override_reason,
            reviewer_note=record.reviewer_note,
            system_recommendation_at_decision=SystemRecommendationSnapshot(
                priority_level=PriorityLevel(record.system_priority_level),
                total_score=record.system_total_score,
                formula_version=record.system_formula_version,
                demand_score=record.system_demand_score,
                impact_score=record.system_impact_score,
                urgency_score=record.system_urgency_score,
                strategic_alignment_score=record.system_strategic_alignment_score,
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
