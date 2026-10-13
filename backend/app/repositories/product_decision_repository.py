from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models import ProductDecision


class ProductDecisionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_request_id(self, feature_request_id: str) -> Optional[ProductDecision]:
        stmt = select(ProductDecision).where(ProductDecision.feature_request_id == feature_request_id)
        return self._session.scalar(stmt)

    def upsert(
        self,
        *,
        feature_request_id: str,
        priority_assessment_id: str,
        decision: str,
        system_priority_level: str,
        system_total_score: int,
        system_formula_version: str,
        system_demand_score: int,
        system_impact_score: int,
        system_urgency_score: int,
        system_strategic_alignment_score: int,
        reviewer_priority: Optional[str] = None,
        override_reason: Optional[str] = None,
        reviewer_note: Optional[str] = None,
    ) -> ProductDecision:
        existing = self.get_by_request_id(feature_request_id)
        if existing is None:
            record = ProductDecision(
                feature_request_id=feature_request_id,
                priority_assessment_id=priority_assessment_id,
                decision=decision,
                reviewer_priority=reviewer_priority,
                override_reason=override_reason,
                reviewer_note=reviewer_note,
                system_priority_level=system_priority_level,
                system_total_score=system_total_score,
                system_formula_version=system_formula_version,
                system_demand_score=system_demand_score,
                system_impact_score=system_impact_score,
                system_urgency_score=system_urgency_score,
                system_strategic_alignment_score=system_strategic_alignment_score,
            )
            self._session.add(record)
        else:
            existing.priority_assessment_id = priority_assessment_id
            existing.decision = decision
            existing.reviewer_priority = reviewer_priority
            existing.override_reason = override_reason
            existing.reviewer_note = reviewer_note
            existing.system_priority_level = system_priority_level
            existing.system_total_score = system_total_score
            existing.system_formula_version = system_formula_version
            existing.system_demand_score = system_demand_score
            existing.system_impact_score = system_impact_score
            existing.system_urgency_score = system_urgency_score
            existing.system_strategic_alignment_score = system_strategic_alignment_score
            record = existing
        self._session.commit()
        self._session.refresh(record)
        return record
