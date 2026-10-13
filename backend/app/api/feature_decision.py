from fastapi import APIRouter, Depends

from app.api.deps import get_product_decision_service
from app.schemas.product_decision import ProductDecisionCreate, ProductDecisionResponse
from app.services.product_decision_service import ProductDecisionService

router = APIRouter(prefix="/feature-requests", tags=["product-decision"])


@router.post("/{request_id}/decision", response_model=ProductDecisionResponse)
def create_product_decision(
    request_id: str,
    body: ProductDecisionCreate,
    service: ProductDecisionService = Depends(get_product_decision_service),
) -> ProductDecisionResponse:
    return service.create_decision(request_id, body)


@router.get("/{request_id}/decision", response_model=ProductDecisionResponse)
def get_product_decision(
    request_id: str,
    service: ProductDecisionService = Depends(get_product_decision_service),
) -> ProductDecisionResponse:
    return service.get_decision(request_id)
