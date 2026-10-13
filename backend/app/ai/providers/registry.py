from dataclasses import dataclass
from typing import Optional

from app.ai.providers.base import AIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import Settings


@dataclass
class ProviderRegistry:
    openai: Optional[AIProvider]
    gemini: Optional[AIProvider]


_registry_override: Optional[ProviderRegistry] = None


def set_provider_registry(registry: ProviderRegistry) -> None:
    global _registry_override
    _registry_override = registry


def clear_provider_registry() -> None:
    global _registry_override
    _registry_override = None


def build_provider_registry(settings: Settings) -> ProviderRegistry:
    if _registry_override is not None:
        return _registry_override

    openai_provider: Optional[AIProvider] = None
    gemini_provider: Optional[AIProvider] = None
    timeout = float(settings.ai_request_timeout_seconds)

    if settings.openai_api_key and settings.openai_model:
        openai_provider = OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=timeout,
        )
    if settings.gemini_api_key:
        gemini_provider = GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            timeout_seconds=timeout,
        )
    return ProviderRegistry(openai=openai_provider, gemini=gemini_provider)


def get_provider_registry(settings: Settings) -> ProviderRegistry:
    return build_provider_registry(settings)
