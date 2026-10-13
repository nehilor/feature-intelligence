import json
from typing import Any

from google.genai import types

from app.ai.prompts.decision_brief_v1 import SYSTEM_INSTRUCTION
from app.ai.providers.decision_brief_base import DecisionBriefCallResult, DecisionBriefEvidenceContext
from app.ai.providers.decision_brief_prompt import format_decision_brief_user_message
from app.ai.providers.errors import (
    ProviderInvalidOutputError,
    ProviderMisconfiguredError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderTransportError,
)
from app.schemas.decision_brief import DecisionBriefOutput


class GeminiDecisionBriefProvider:
    provider_name = "gemini"

    def __init__(self, client, model: str) -> None:
        if not model:
            raise ProviderMisconfiguredError("Gemini model is not configured")
        self._client = client
        self._model = model

    def generate_brief(self, context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult:
        user_content = format_decision_brief_user_message(context)
        schema = DecisionBriefOutput.model_json_schema()
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
            validated = DecisionBriefOutput.model_validate(payload)
        except Exception as exc:
            raise ProviderInvalidOutputError(str(exc)) from exc

        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        output_tokens = getattr(usage, "candidates_token_count", None) if usage else None
        return DecisionBriefCallResult(
            output=validated,
            provider=self.provider_name,
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
