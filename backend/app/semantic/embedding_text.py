import hashlib
from typing import Optional


def build_canonical_embedding_text(
    title: str,
    description: str,
    underlying_need: Optional[str] = None,
) -> str:
    text = f"Title: {title.strip()}\n\nDescription:\n{description.strip()}"
    if underlying_need and underlying_need.strip():
        text += f"\n\nUnderlying need:\n{underlying_need.strip()}"
    return text


def compute_embedding_content_hash(provider: str, model: str, canonical_text: str) -> str:
    payload = f"{provider}\n{model}\n{canonical_text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
