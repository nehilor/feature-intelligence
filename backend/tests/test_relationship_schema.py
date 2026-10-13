import pytest
from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType
from app.schemas.relationship import RelationshipClassificationOutput
from pydantic import ValidationError


def test_valid_duplicate_related_distinct() -> None:
    for rel in RequestRelationshipType:
        model = RelationshipClassificationOutput(
            relationship=rel,
            confidence=RelationshipConfidence.HIGH,
            reason="Evidence.",
        )
        assert model.relationship == rel


@pytest.mark.parametrize(
    "field,bad",
    [
        ("relationship", "MERGE"),
        ("confidence", "VERY_HIGH"),
    ],
)
def test_invalid_enum_rejected(field: str, bad: str) -> None:
    payload = {
        "relationship": RequestRelationshipType.RELATED.value,
        "confidence": RelationshipConfidence.MEDIUM.value,
        "reason": "Evidence.",
    }
    payload[field] = bad
    with pytest.raises(ValidationError):
        RelationshipClassificationOutput.model_validate(payload)


def test_reason_required() -> None:
    with pytest.raises(ValidationError):
        RelationshipClassificationOutput(
            relationship=RequestRelationshipType.DISTINCT,
            confidence=RelationshipConfidence.LOW,
            reason="",
        )
