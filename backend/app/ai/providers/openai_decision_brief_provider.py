import json
from typing import Any

from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.ai.prompts.decision_brief_v1 import SYSTEM_INSTRUCTION
from app.ai.providers.decision_brief_base import DecisionBriefCallResult, DecisionBriefEvidenceContext
from app.ai.providers.decision_brief_prompt import format_decision_brief_user_message
from app.ai.providers.errors import (
    ProviderInvalidOutputError,
    ProviderMisconfiguredError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderTransportError,
)
from app.schemas.decision_brief import DecisionBriefOutput


class OpenAIDecisionBriefProvider:
    provider_name = "openai"

    def __init__(self, client, model: str) -> None:
        if not model:
            raise ProviderMisconfiguredError("OpenAI model is not configured")
        self._client = client
        self._model = model

    def generate_brief(self, context: DecisionBriefEvidenceContext) -> DecisionBriefCallResult:
        user_content = format_decision_brief_user_message(context)
        schema = DecisionBriefOutput.model_json_schema()
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
                        "name": "decision_brief",
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
            validated = DecisionBriefOutput.model_validate(payload)
        except Exception as exc:
            raise ProviderInvalidOutputError(str(exc)) from exc

        usage = response.usage
        return DecisionBriefCallResult(
            output=validated,
            provider=self.provider_name,
            model=self._model,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )
