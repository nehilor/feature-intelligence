from app.ai.embeddings.base import EmbeddingResult
from app.semantic.vector_validation import validate_embedding_vector
from openai import APITimeoutError, OpenAI


class EmbeddingProviderError(Exception):
    pass


class OpenAIEmbeddingProvider:
    provider_name = "openai"

    def __init__(self, api_key: str, model: str, timeout_seconds: float) -> None:
        if not api_key:
            raise EmbeddingProviderError("OpenAI API key is not configured")
        self.model = model
        self._client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    def embed_text(self, text: str) -> EmbeddingResult:
        try:
            response = self._client.embeddings.create(model=self.model, input=text)
        except APITimeoutError as exc:
            raise EmbeddingProviderError(str(exc)) from exc
        except Exception as exc:
            raise EmbeddingProviderError(str(exc)) from exc
        if not response.data:
            raise EmbeddingProviderError("OpenAI returned no embedding data")
        vector = validate_embedding_vector(response.data[0].embedding)
        return EmbeddingResult(vector=vector, provider=self.provider_name, model=self.model)
