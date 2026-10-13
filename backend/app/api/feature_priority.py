from fastapi import APIRouter, Depends

from app.api.deps import get_priority_service
from app.schemas.priority import PriorityAssessmentResponse, PriorityCalculateRequest
from app.services.priority_service import PriorityService

router = APIRouter(prefix="/feature-requests", tags=["priority"])


@router.post("/{request_id}/priority", response_model=PriorityAssessmentResponse)
def calculate_priority(
    request_id: str,
    body: PriorityCalculateRequest,
    service: PriorityService = Depends(get_priority_service),
) -> PriorityAssessmentResponse:
    return service.calculate_priority(request_id, body.strategic_alignment)


@router.get("/{request_id}/priority", response_model=PriorityAssessmentResponse)
def get_priority(
    request_id: str,
    service: PriorityService = Depends(get_priority_service),
) -> PriorityAssessmentResponse:
    return service.get_priority(request_id)
