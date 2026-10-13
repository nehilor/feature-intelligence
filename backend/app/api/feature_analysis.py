from fastapi import APIRouter, Depends

from app.api.deps import get_feature_triage_service
from app.schemas.triage import FeatureAnalysisResponse
from app.services.feature_triage_service import FeatureTriageService

router = APIRouter(prefix="/feature-requests", tags=["feature-analysis"])


@router.post("/{request_id}/analysis", response_model=FeatureAnalysisResponse)
def analyze_feature_request(
    request_id: str,
    service: FeatureTriageService = Depends(get_feature_triage_service),
) -> FeatureAnalysisResponse:
    return service.analyze(request_id)


@router.get("/{request_id}/analysis", response_model=FeatureAnalysisResponse)
def get_feature_analysis(
    request_id: str,
    service: FeatureTriageService = Depends(get_feature_triage_service),
) -> FeatureAnalysisResponse:
    return service.get_analysis(request_id)
