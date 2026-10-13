import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.ai.prompts.feature_triage_v1 import SYSTEM_INSTRUCTION, USER_TEMPLATE
from app.ai.providers.base import ProviderCallResult
from app.ai.providers.errors import (
    ProviderInvalidOutputError,
    ProviderMisconfiguredError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderTransportError,
)
from app.schemas.triage import TriageAnalysisOutput

logger = logging.getLogger("app.ai")


class GeminiProvider:
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str, timeout_seconds: float) -> None:
        if not api_key:
            raise ProviderMisconfiguredError("Gemini API key is not configured")
        if not model:
            raise ProviderMisconfiguredError("Gemini model is not configured")
        self._model = model
        self._client = genai.Client(api_key=api_key, http_options={"timeout": timeout_seconds * 1000})

    def analyze_feature_request(self, title: str, description: str) -> ProviderCallResult:
        user_content = USER_TEMPLATE.format(title=title, description=description)
        schema = TriageAnalysisOutput.model_json_schema()
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        except TimeoutError as exc:
            raise ProviderTimeoutError(str(exc)) from exc
        except ConnectionError as exc:
            raise ProviderTransportError(str(exc)) from exc
        except Exception as exc:
            raise ProviderServerError(str(exc)) from exc

        text = response.text
        if not text:
            raise ProviderInvalidOutputError("Gemini returned empty content")
        try:
            payload: Any = json.loads(text)
            validated = TriageAnalysisOutput.model_validate(payload)
        except Exception as exc:
            raise ProviderInvalidOutputError(str(exc)) from exc

        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        output_tokens = getattr(usage, "candidates_token_count", None) if usage else None
        return ProviderCallResult(
            output=validated,
            provider=self.provider_name,
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
