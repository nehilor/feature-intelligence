from dataclasses import dataclass
from typing import Optional, Protocol

from app.schemas.triage import TriageAnalysisOutput


@dataclass
class ProviderCallResult:
    output: TriageAnalysisOutput
    provider: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class AIProvider(Protocol):
    provider_name: str

    def analyze_feature_request(self, title: str, description: str) -> ProviderCallResult:
        ...
