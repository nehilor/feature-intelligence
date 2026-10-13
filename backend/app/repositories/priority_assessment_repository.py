from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models import PriorityAssessment


class PriorityAssessmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_request_id(self, feature_request_id: str) -> Optional[PriorityAssessment]:
        stmt = select(PriorityAssessment).where(PriorityAssessment.feature_request_id == feature_request_id)
        return self._session.scalar(stmt)

    def upsert(
        self,
        *,
        feature_request_id: str,
        support_count: int,
        relationship_signal_count: int,
        demand_score: int,
        impact_score: int,
        urgency_score: int,
        strategic_alignment: str,
        strategic_alignment_score: int,
        total_score: int,
        priority_level: str,
        evidence_completeness: str,
        formula_version: str,
    ) -> PriorityAssessment:
        existing = self.get_by_request_id(feature_request_id)
        if existing is None:
            record = PriorityAssessment(
                feature_request_id=feature_request_id,
                support_count=support_count,
                relationship_signal_count=relationship_signal_count,
                demand_score=demand_score,
                impact_score=impact_score,
                urgency_score=urgency_score,
                strategic_alignment=strategic_alignment,
                strategic_alignment_score=strategic_alignment_score,
                total_score=total_score,
                priority_level=priority_level,
                evidence_completeness=evidence_completeness,
                formula_version=formula_version,
            )
            self._session.add(record)
        else:
            existing.support_count = support_count
            existing.relationship_signal_count = relationship_signal_count
            existing.demand_score = demand_score
            existing.impact_score = impact_score
            existing.urgency_score = urgency_score
            existing.strategic_alignment = strategic_alignment
            existing.strategic_alignment_score = strategic_alignment_score
            existing.total_score = total_score
            existing.priority_level = priority_level
            existing.evidence_completeness = evidence_completeness
            existing.formula_version = formula_version
            record = existing
        self._session.commit()
        self._session.refresh(record)
        return record
