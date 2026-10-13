import json
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models import DecisionBrief


class DecisionBriefRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_request_id(self, feature_request_id: str) -> Optional[DecisionBrief]:
        stmt = select(DecisionBrief).where(DecisionBrief.feature_request_id == feature_request_id)
        return self._session.scalar(stmt)

    def upsert(
        self,
        *,
        feature_request_id: str,
        priority_assessment_id: str,
        problem: str,
        evidence_summary: str,
        why_it_matters: str,
        risks_and_unknowns: List[str],
        recommended_next_step: str,
        provider: str,
        model: str,
        prompt_version: str,
    ) -> DecisionBrief:
        existing = self.get_by_request_id(feature_request_id)
        payload = json.dumps(risks_and_unknowns)
        if existing is None:
            record = DecisionBrief(
                feature_request_id=feature_request_id,
                priority_assessment_id=priority_assessment_id,
                problem=problem,
                evidence_summary=evidence_summary,
                why_it_matters=why_it_matters,
                risks_and_unknowns_json=payload,
                recommended_next_step=recommended_next_step,
                provider=provider,
                model=model,
                prompt_version=prompt_version,
            )
            self._session.add(record)
        else:
            existing.priority_assessment_id = priority_assessment_id
            existing.problem = problem
            existing.evidence_summary = evidence_summary
            existing.why_it_matters = why_it_matters
            existing.risks_and_unknowns_json = payload
            existing.recommended_next_step = recommended_next_step
            existing.provider = provider
            existing.model = model
            existing.prompt_version = prompt_version
            record = existing
        self._session.commit()
        self._session.refresh(record)
        return record
