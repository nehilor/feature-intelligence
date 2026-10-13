from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.ai_enums import AIProcessingState
from app.persistence.models import FeatureAnalysis


class FeatureAnalysisRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_request_id(self, feature_request_id: str) -> Optional[FeatureAnalysis]:
        stmt = select(FeatureAnalysis).where(FeatureAnalysis.feature_request_id == feature_request_id)
        return self._session.scalar(stmt)

    def upsert(
        self,
        *,
        feature_request_id: str,
        processing_state: AIProcessingState,
        summary: Optional[str] = None,
        underlying_need: Optional[str] = None,
        theme: Optional[str] = None,
        customer_impact: Optional[str] = None,
        urgency: Optional[str] = None,
        confidence: Optional[str] = None,
        rationale: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        prompt_version: Optional[str] = None,
        used_fallback: bool = False,
    ) -> FeatureAnalysis:
        existing = self.get_by_request_id(feature_request_id)
        if existing is None:
            record = FeatureAnalysis(
                feature_request_id=feature_request_id,
                processing_state=processing_state.value,
                summary=summary,
                underlying_need=underlying_need,
                theme=theme,
                customer_impact=customer_impact,
                urgency=urgency,
                confidence=confidence,
                rationale=rationale,
                provider=provider,
                model=model,
                prompt_version=prompt_version,
                used_fallback=used_fallback,
            )
            self._session.add(record)
        else:
            existing.processing_state = processing_state.value
            existing.summary = summary
            existing.underlying_need = underlying_need
            existing.theme = theme
            existing.customer_impact = customer_impact
            existing.urgency = urgency
            existing.confidence = confidence
            existing.rationale = rationale
            existing.provider = provider
            existing.model = model
            existing.prompt_version = prompt_version
            existing.used_fallback = used_fallback
            record = existing
        self._session.commit()
        self._session.refresh(record)
        return record
