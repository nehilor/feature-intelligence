from fastapi import APIRouter, Depends

from app.api.deps import get_decision_brief_service
from app.schemas.decision_brief import DecisionBriefResponse
from app.services.decision_brief_service import DecisionBriefService

router = APIRouter(prefix="/feature-requests", tags=["decision-brief"])


@router.post("/{request_id}/decision-brief", response_model=DecisionBriefResponse)
def generate_decision_brief(
    request_id: str,
    service: DecisionBriefService = Depends(get_decision_brief_service),
) -> DecisionBriefResponse:
    return service.generate_brief(request_id)


@router.get("/{request_id}/decision-brief", response_model=DecisionBriefResponse)
def get_decision_brief(
    request_id: str,
    service: DecisionBriefService = Depends(get_decision_brief_service),
) -> DecisionBriefResponse:
    return service.get_brief(request_id)
