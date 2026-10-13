import pytest
from app.domain.ai_enums import AnalysisConfidence, CustomerImpact, Theme, Urgency
from app.schemas.triage import TriageAnalysisOutput
from pydantic import ValidationError


def _valid_payload() -> dict:
    return {
        "summary": "Summary text.",
        "underlying_need": "Underlying need text.",
        "theme": Theme.REPORTING_AND_DATA.value,
        "customer_impact": CustomerImpact.HIGH.value,
        "urgency": Urgency.UNKNOWN.value,
        "confidence": AnalysisConfidence.HIGH.value,
        "rationale": "Evidence-based rationale.",
    }


def test_valid_structured_output_accepted() -> None:
    model = TriageAnalysisOutput.model_validate(_valid_payload())
    assert model.theme == Theme.REPORTING_AND_DATA


def test_valid_theme_values_accepted() -> None:
    for theme in Theme:
        payload = _valid_payload()
        payload["theme"] = theme.value
        assert TriageAnalysisOutput.model_validate(payload).theme == theme


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("theme", "NOT_A_THEME"),
        ("customer_impact", "CRITICAL"),
        ("urgency", "IMMEDIATE"),
        ("confidence", "VERY_HIGH"),
    ],
)
def test_invalid_enum_rejected(field: str, bad_value: str) -> None:
    payload = _valid_payload()
    payload[field] = bad_value
    with pytest.raises(ValidationError):
        TriageAnalysisOutput.model_validate(payload)


def test_missing_required_fields_rejected() -> None:
    payload = _valid_payload()
    del payload["summary"]
    with pytest.raises(ValidationError):
        TriageAnalysisOutput.model_validate(payload)
