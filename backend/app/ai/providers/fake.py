from dataclasses import dataclass
from typing import Callable, Optional

from app.ai.providers.base import ProviderCallResult
from app.ai.providers.errors import ProviderError, ProviderInvalidOutputError, ProviderTimeoutError
from app.domain.ai_enums import AnalysisConfidence, CustomerImpact, Theme, Urgency
from app.schemas.triage import TriageAnalysisOutput


def _default_output() -> TriageAnalysisOutput:
    return TriageAnalysisOutput(
        summary="Finance users need easier access to reporting data outside the platform.",
        underlying_need=("Finance teams need reporting data for external reconciliation and downstream analysis."),
        theme=Theme.REPORTING_AND_DATA,
        customer_impact=CustomerImpact.HIGH,
        urgency=Urgency.UNKNOWN,
        confidence=AnalysisConfidence.HIGH,
        rationale="The request describes a recurring finance workflow that depends on external reporting.",
    )


@dataclass
class FakeProvider:
    provider_name: str
    model: str
    behavior: Optional[Callable[[], ProviderCallResult]] = None
    call_count: int = 0

    def analyze_feature_request(self, title: str, description: str) -> ProviderCallResult:
        self.call_count += 1
        if self.behavior is None:
            return ProviderCallResult(
                output=_default_output(),
                provider=self.provider_name,
                model=self.model,
            )
        return self.behavior()


def fake_success(provider: str, model: str) -> FakeProvider:
    def behavior() -> ProviderCallResult:
        result = _default_output()
        return ProviderCallResult(output=result, provider=provider, model=model)

    return FakeProvider(provider_name=provider, model=model, behavior=behavior)


def fake_timeout(provider: str, model: str) -> FakeProvider:
    def behavior() -> ProviderCallResult:
        raise ProviderTimeoutError("fake timeout")

    return FakeProvider(provider_name=provider, model=model, behavior=behavior)


def fake_invalid_output(provider: str, model: str, times: int = 2) -> FakeProvider:
    state = {"count": 0}

    def behavior() -> ProviderCallResult:
        state["count"] += 1
        if state["count"] <= times:
            raise ProviderInvalidOutputError("fake invalid output")
        return ProviderCallResult(output=_default_output(), provider=provider, model=model)

    return FakeProvider(provider_name=provider, model=model, behavior=behavior)


def fake_failure(provider: str, model: str, error: Optional[ProviderError] = None) -> FakeProvider:
    def behavior() -> ProviderCallResult:
        raise error or ProviderError("fake provider failure")

    return FakeProvider(provider_name=provider, model=model, behavior=behavior)
