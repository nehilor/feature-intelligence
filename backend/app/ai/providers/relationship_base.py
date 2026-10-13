from dataclasses import dataclass
from typing import Optional, Protocol

from app.schemas.relationship import RelationshipClassificationOutput


@dataclass
class RelationshipRequestContext:
    title: str
    description: str
    underlying_need: Optional[str] = None


@dataclass
class RelationshipCallResult:
    output: RelationshipClassificationOutput
    provider: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class RelationshipProvider(Protocol):
    provider_name: str

    def classify_relationship(
        self,
        target: RelationshipRequestContext,
        candidate: RelationshipRequestContext,
    ) -> RelationshipCallResult: ...
