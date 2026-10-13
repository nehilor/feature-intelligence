from typing import Optional

from fastapi import HTTPException, status

from app.domain.enums import FeatureRequestStatus
from app.repositories.feature_request_repository import (
    FeatureRequestRepository,
    normalize_pagination,
)
from app.schemas.feature_request import (
    FeatureRequestCreate,
    FeatureRequestListResponse,
    FeatureRequestResponse,
    SupportRequest,
    SupportResponse,
)


class FeatureRequestService:
    def __init__(self, repository: FeatureRequestRepository) -> None:
        self._repository = repository

    def create(self, payload: FeatureRequestCreate) -> FeatureRequestResponse:
        created = self._repository.create(payload.title, payload.description)
        return self._to_response(created, support_count=0, supporter_key=None)

    def get(self, request_id: str, supporter_key: Optional[str]) -> FeatureRequestResponse:
        request = self._repository.get_by_id(request_id)
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feature request not found",
            )
        support_count = self._repository.count_support(request_id)
        return self._to_response(request, support_count=support_count, supporter_key=supporter_key)

    def list(
        self,
        *,
        q: Optional[str],
        sort: str,
        limit: Optional[int],
        offset: Optional[int],
        supporter_key: Optional[str],
    ) -> FeatureRequestListResponse:
        if sort not in {"recent", "supported"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid sort value",
            )
        try:
            resolved_limit, resolved_offset = normalize_pagination(limit, offset)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        rows, total = self._repository.list_requests(
            q=q,
            sort=sort,
            limit=resolved_limit,
            offset=resolved_offset,
        )
        items = [
            self._to_response(request, support_count=count, supporter_key=supporter_key)
            for request, count in rows
        ]
        return FeatureRequestListResponse(
            items=items,
            total=total,
            limit=resolved_limit,
            offset=resolved_offset,
        )

    def support(self, request_id: str, payload: SupportRequest) -> SupportResponse:
        request = self._repository.get_by_id(request_id)
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feature request not found",
            )

        new_support = self._repository.add_support_signal(request_id, payload.supporter_key)
        support_count = self._repository.count_support(request_id)
        return SupportResponse(
            feature_request_id=request_id,
            supported=True,
            new_support=new_support,
            support_count=support_count,
        )

    def _to_response(
        self,
        request,
        *,
        support_count: int,
        supporter_key: Optional[str],
    ) -> FeatureRequestResponse:
        supported_by_current_user = None
        if supporter_key:
            supported_by_current_user = self._repository.has_support(request.id, supporter_key)
        return FeatureRequestResponse(
            id=request.id,
            title=request.title,
            description=request.description,
            status=FeatureRequestStatus(request.status),
            support_count=support_count,
            created_at=request.created_at,
            updated_at=request.updated_at,
            supported_by_current_user=supported_by_current_user,
        )
