from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models import FeatureEmbedding


class FeatureEmbeddingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_request_id(self, feature_request_id: str) -> Optional[FeatureEmbedding]:
        stmt = select(FeatureEmbedding).where(FeatureEmbedding.feature_request_id == feature_request_id)
        return self._session.scalar(stmt)

    def list_all(self) -> List[FeatureEmbedding]:
        return list(self._session.scalars(select(FeatureEmbedding)).all())

    def upsert(
        self,
        *,
        feature_request_id: str,
        embedding_json: str,
        provider: str,
        model: str,
        content_hash: str,
    ) -> FeatureEmbedding:
        existing = self.get_by_request_id(feature_request_id)
        if existing is None:
            record = FeatureEmbedding(
                feature_request_id=feature_request_id,
                embedding=embedding_json,
                provider=provider,
                model=model,
                content_hash=content_hash,
            )
            self._session.add(record)
        else:
            existing.embedding = embedding_json
            existing.provider = provider
            existing.model = model
            existing.content_hash = content_hash
            record = existing
        self._session.commit()
        self._session.refresh(record)
        return record
