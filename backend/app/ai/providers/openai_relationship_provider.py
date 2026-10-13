import json
from typing import Any

from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.ai.prompts.relationship_classification_v1 import SYSTEM_INSTRUCTION
from app.ai.providers.errors import (
    ProviderInvalidOutputError,
    ProviderMisconfiguredError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderTransportError,
)
from app.ai.providers.relationship_base import RelationshipCallResult, RelationshipRequestContext
from app.ai.providers.relationship_prompt import format_relationship_user_message
from app.schemas.relationship import RelationshipClassificationOutput


class OpenAIRelationshipProvider:
    provider_name = "openai"

    def __init__(self, client, model: str) -> None:
        if not model:
            raise ProviderMisconfiguredError("OpenAI model is not configured")
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
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_content},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "relationship_classification",
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
            validated = RelationshipClassificationOutput.model_validate(payload)
        except Exception as exc:
            raise ProviderInvalidOutputError(str(exc)) from exc

        usage = response.usage
        return RelationshipCallResult(
            output=validated,
            provider=self.provider_name,
            model=self._model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )
