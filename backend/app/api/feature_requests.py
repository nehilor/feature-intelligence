from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_feature_request_service
from app.schemas.feature_request import (
    FeatureRequestCreate,
    FeatureRequestListResponse,
    FeatureRequestResponse,
    SupportRequest,
    SupportResponse,
)
from app.services.feature_request_service import FeatureRequestService

router = APIRouter(prefix="/feature-requests", tags=["feature-requests"])


@router.post("", response_model=FeatureRequestResponse, status_code=status.HTTP_201_CREATED)
def create_feature_request(
    payload: FeatureRequestCreate,
    service: FeatureRequestService = Depends(get_feature_request_service),
) -> FeatureRequestResponse:
    return service.create(payload)


@router.get("", response_model=FeatureRequestListResponse)
def list_feature_requests(
    q: Optional[str] = Query(default=None),
    sort: str = Query(default="recent"),
    limit: Optional[int] = Query(default=None),
    offset: Optional[int] = Query(default=None),
    supporter_key: Optional[str] = Query(default=None),
    service: FeatureRequestService = Depends(get_feature_request_service),
) -> FeatureRequestListResponse:
    return service.list(q=q, sort=sort, limit=limit, offset=offset, supporter_key=supporter_key)


@router.get("/{request_id}", response_model=FeatureRequestResponse)
def get_feature_request(
    request_id: str,
    supporter_key: Optional[str] = Query(default=None),
    service: FeatureRequestService = Depends(get_feature_request_service),
) -> FeatureRequestResponse:
    return service.get(request_id, supporter_key)


@router.post("/{request_id}/support", response_model=SupportResponse)
def support_feature_request(
    request_id: str,
    payload: SupportRequest,
    service: FeatureRequestService = Depends(get_feature_request_service),
) -> SupportResponse:
    return service.support(request_id, payload)
