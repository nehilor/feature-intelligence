from typing import Callable

from app.ai.providers.decision_brief_base import (
    DecisionBriefCallResult,
    DecisionBriefEvidenceContext,
)
from app.ai.providers.errors import ProviderInvalidOutputError
from app.schemas.decision_brief import DecisionBriefOutput


class FakeDecisionBriefProvider:
    provider_name: str

    def __init__(
        self,
        name: str,
        handler: Callable[[DecisionBriefEvidenceContext], DecisionBriefCallResult],
    ) -> None:
        self.provider_name = name
        self._handler = handler
        self.call_count = 0

    def generate_brief(self, context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult:
        self.call_count += 1
        return self._handler(context)


def fake_brief_success(name: str, model: str) -> FakeDecisionBriefProvider:
    def _handler(_context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult:
        return DecisionBriefCallResult(
            output=DecisionBriefOutput(
                problem="Teams need reporting outside the platform.",
                evidence_summary="Direct support and related reporting requests exist.",
                why_it_matters="Manual reconciliation creates recurring work.",
                risks_and_unknowns=["Export formats need discovery."],
                recommended_next_step="Run product discovery for consolidated export.",
            ),
            provider=name,
            model=model,
        )

    return FakeDecisionBriefProvider(name, _handler)


def fake_brief_failure(name: str, model: str, error: Exception) -> FakeDecisionBriefProvider:
    def _handler(_context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult:
        raise error

    return FakeDecisionBriefProvider(name, _handler)


def fake_brief_invalid(name: str, model: str) -> FakeDecisionBriefProvider:
    def _handler(_context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult:
        raise ProviderInvalidOutputError("invalid brief output")

    return FakeDecisionBriefProvider(name, _handler)
