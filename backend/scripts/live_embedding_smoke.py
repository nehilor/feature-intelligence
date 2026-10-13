"""Optional live OpenAI embedding smoke test (not part of make verify)."""

from __future__ import annotations

import os
import sys

from app.ai.embeddings.registry import get_embedding_provider
from app.core.config import get_settings
from app.semantic.embedding_text import build_canonical_embedding_text
from app.semantic.vector_validation import validate_embedding_vector


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY required for live embedding smoke test.")
        return 0
    get_settings.cache_clear()
    provider = get_embedding_provider(get_settings())
    if provider is None:
        print("SKIP: embedding provider not configured.")
        return 0
    text = build_canonical_embedding_text(
        "Export reports to CSV",
        "Finance team exports reporting data for reconciliation.",
    )
    result = provider.embed_text(text)
    vector = validate_embedding_vector(result.vector)
    print(f"embedding_dimensions={len(vector)} provider={result.provider} model={result.model}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
