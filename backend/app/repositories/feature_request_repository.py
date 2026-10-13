from typing import Optional

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.enums import FeatureRequestStatus
from app.domain.validation import DEFAULT_LIST_LIMIT, MAX_LIST_LIMIT
from app.persistence.models import FeatureRequest, SupportSignal


class FeatureRequestRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, title: str, description: str) -> FeatureRequest:
        request = FeatureRequest(
            title=title,
            description=description,
            status=FeatureRequestStatus.SUBMITTED.value,
        )
        self._session.add(request)
        self._session.commit()
        self._session.refresh(request)
        return request

    def get_by_id(self, request_id: str) -> Optional[FeatureRequest]:
        return self._session.get(FeatureRequest, request_id)

    def list_requests(
        self,
        *,
        q: Optional[str],
        sort: str,
        limit: int,
        offset: int,
    ) -> tuple[list[tuple[FeatureRequest, int]], int]:
        support_count_expr = func.count(SupportSignal.id).label("support_count")
        stmt: Select = (
            select(FeatureRequest, support_count_expr)
            .outerjoin(SupportSignal, SupportSignal.feature_request_id == FeatureRequest.id)
            .group_by(FeatureRequest.id)
        )

        filters = []
        if q:
            needle = f"%{q.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(FeatureRequest.title).like(needle),
                    func.lower(FeatureRequest.description).like(needle),
                )
            )
            stmt = stmt.where(filters[0])

        count_stmt = select(func.count(FeatureRequest.id))
        if filters:
            count_stmt = count_stmt.where(filters[0])
        total = int(self._session.scalar(count_stmt) or 0)

        if sort == "supported":
            stmt = stmt.order_by(support_count_expr.desc(), FeatureRequest.created_at.desc())
        else:
            stmt = stmt.order_by(FeatureRequest.created_at.desc())

        rows = self._session.execute(stmt.limit(limit).offset(offset)).all()
        return [(row[0], int(row[1])) for row in rows], int(total)

    def count_support(self, request_id: str) -> int:
        stmt = select(func.count(SupportSignal.id)).where(
            SupportSignal.feature_request_id == request_id
        )
        return int(self._session.scalar(stmt) or 0)

    def has_support(self, request_id: str, supporter_key: str) -> bool:
        stmt = select(SupportSignal.id).where(
            SupportSignal.feature_request_id == request_id,
            SupportSignal.supporter_key == supporter_key,
        )
        return self._session.scalar(stmt) is not None

    def add_support_signal(self, request_id: str, supporter_key: str) -> bool:
        signal = SupportSignal(feature_request_id=request_id, supporter_key=supporter_key)
        self._session.add(signal)
        try:
            self._session.commit()
            return True
        except IntegrityError:
            self._session.rollback()
            return False


def normalize_pagination(limit: Optional[int], offset: Optional[int]) -> tuple[int, int]:
    resolved_limit = DEFAULT_LIST_LIMIT if limit is None else limit
    resolved_offset = 0 if offset is None else offset
    if resolved_limit < 1 or resolved_limit > MAX_LIST_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIST_LIMIT}")
    if resolved_offset < 0:
        raise ValueError("offset must be non-negative")
    return resolved_limit, resolved_offset
