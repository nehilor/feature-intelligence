import json
from typing import Any

from google.genai import types

from app.ai.prompts.relationship_classification_v1 import SYSTEM_INSTRUCTION
from app.ai.providers.errors import (
    ProviderInvalidOutputError,
    ProviderMisconfiguredError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderTransportError,
)
from app.ai.providers.relationship_base import RelationshipCallResult, RelationshipRequestContext
from app.ai.providers.relationship_prompt import format_relationship_user_message
from app.schemas.relationship import RelationshipClassificationOutput


class GeminiRelationshipProvider:
    provider_name = "gemini"

    def __init__(self, client, model: str) -> None:
        if not model:
            raise ProviderMisconfiguredError("Gemini model is not configured")
        self._client = client
        self._model = model

    def classify_relationship(
        self,
        target: RelationshipRequestContext,
        candidate: RelationshipRequestContext,
    ) -> RelationshipCallResult:
        user_content = format_relationship_user_message(target, candidate)
        schema = RelationshipClassificationOutput.model_json_schema()
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
            validated = RelationshipClassificationOutput.model_validate(payload)
        except Exception as exc:
            raise ProviderInvalidOutputError(str(exc)) from exc

        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        output_tokens = getattr(usage, "candidates_token_count", None) if usage else None
        return RelationshipCallResult(
            output=validated,
            provider=self.provider_name,
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
