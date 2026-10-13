from dataclasses import dataclass
from typing import Callable, Optional

from app.ai.providers.relationship_base import RelationshipCallResult, RelationshipRequestContext
from app.domain.relationship_enums import RelationshipConfidence, RequestRelationshipType
from app.schemas.relationship import RelationshipClassificationOutput


@dataclass
class FakeRelationshipProvider:
    provider_name: str
    model: str
    behavior: Optional[Callable[[RelationshipRequestContext, RelationshipRequestContext], RelationshipCallResult]] = (
        None
    )
    call_count: int = 0

    def classify_relationship(
        self,
        target: RelationshipRequestContext,
        candidate: RelationshipRequestContext,
    ) -> RelationshipCallResult:
        self.call_count += 1
        if self.behavior is not None:
            return self.behavior(target, candidate)
        return RelationshipCallResult(
            output=RelationshipClassificationOutput(
                relationship=RequestRelationshipType.RELATED,
                confidence=RelationshipConfidence.MEDIUM,
                reason="Fake default related classification.",
            ),
            provider=self.provider_name,
            model=self.model,
        )
