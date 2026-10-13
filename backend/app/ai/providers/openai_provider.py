import json
import logging
from typing import Any

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from app.ai.prompts.feature_triage_v1 import SYSTEM_INSTRUCTION, USER_TEMPLATE
from app.ai.providers.base import ProviderCallResult
from app.ai.providers.errors import (
    ProviderInvalidOutputError,
    ProviderMisconfiguredError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderTransportError,
)
from app.schemas.triage import TriageAnalysisOutput

logger = logging.getLogger("app.ai")


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, api_key: str, model: str, timeout_seconds: float) -> None:
        if not api_key:
            raise ProviderMisconfiguredError("OpenAI API key is not configured")
        if not model:
            raise ProviderMisconfiguredError("OpenAI model is not configured")
        self._model = model
        self._client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    def analyze_feature_request(self, title: str, description: str) -> ProviderCallResult:
        user_content = USER_TEMPLATE.format(title=title, description=description)
        schema = TriageAnalysisOutput.model_json_schema()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_content},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "feature_triage",
                        "schema": schema,
                        "strict": True,
                    },
                },
            )
        except APITimeoutError as exc:
            raise ProviderTimeoutError(str(exc)) from exc
        except APIConnectionError as exc:
            raise ProviderTransportError(str(exc)) from exc
        except RateLimitError as exc:
            raise ProviderRateLimitError(str(exc)) from exc
        except Exception as exc:
            raise ProviderServerError(str(exc)) from exc

        content = response.choices[0].message.content
        if not content:
            raise ProviderInvalidOutputError("OpenAI returned empty content")
        try:
            payload: Any = json.loads(content)
            validated = TriageAnalysisOutput.model_validate(payload)
        except Exception as exc:
            raise ProviderInvalidOutputError(str(exc)) from exc

        usage = response.usage
        return ProviderCallResult(
            output=validated,
            provider=self.provider_name,
            model=self._model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )
