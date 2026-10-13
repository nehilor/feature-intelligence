from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.persistence.models import RequestRelationship


def canonical_pair(request_id_a: str, request_id_b: str) -> tuple:
    if request_id_a <= request_id_b:
        return request_id_a, request_id_b
    return request_id_b, request_id_a


class RequestRelationshipRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_pair(self, request_id_a: str, request_id_b: str) -> Optional[RequestRelationship]:
        a_id, b_id = canonical_pair(request_id_a, request_id_b)
        stmt = select(RequestRelationship).where(
            RequestRelationship.request_a_id == a_id,
            RequestRelationship.request_b_id == b_id,
        )
        return self._session.scalar(stmt)

    def upsert(
        self,
        *,
        request_id_a: str,
        request_id_b: str,
        relationship: str,
        similarity_score: float,
        confidence: str,
        reason: str,
        provider: str,
        model: str,
        prompt_version: str,
    ) -> RequestRelationship:
        a_id, b_id = canonical_pair(request_id_a, request_id_b)
        existing = self.get_pair(a_id, b_id)
        if existing is None:
            record = RequestRelationship(
                request_a_id=a_id,
                request_b_id=b_id,
                relationship=relationship,
                similarity_score=similarity_score,
                confidence=confidence,
                reason=reason,
                provider=provider,
                model=model,
                prompt_version=prompt_version,
            )
            self._session.add(record)
        else:
            existing.relationship = relationship
            existing.similarity_score = similarity_score
            existing.confidence = confidence
            existing.reason = reason
            existing.provider = provider
            existing.model = model
            existing.prompt_version = prompt_version
            record = existing
        self._session.commit()
        self._session.refresh(record)
        return record

    def list_for_request(self, feature_request_id: str) -> List[RequestRelationship]:
        stmt = select(RequestRelationship).where(
            or_(
                RequestRelationship.request_a_id == feature_request_id,
                RequestRelationship.request_b_id == feature_request_id,
            )
        )
        return list(self._session.scalars(stmt).all())
