from app.semantic.embedding_text import build_canonical_embedding_text, compute_embedding_content_hash


def test_canonical_from_title_description() -> None:
    text = build_canonical_embedding_text("Export reports", "Need CSV export.")
    assert "Title: Export reports" in text
    assert "Description:\nNeed CSV export." in text
    assert "Underlying need" not in text


def test_underlying_need_included_when_present() -> None:
    text = build_canonical_embedding_text("T", "D", "Need external reporting.")
    assert "Underlying need:\nNeed external reporting." in text


def test_content_hash_stable() -> None:
    text = build_canonical_embedding_text("A", "B")
    h1 = compute_embedding_content_hash("openai", "text-embedding-3-small", text)
    h2 = compute_embedding_content_hash("openai", "text-embedding-3-small", text)
    assert h1 == h2


def test_content_change_changes_hash() -> None:
    base = build_canonical_embedding_text("A", "B")
    changed = build_canonical_embedding_text("A", "B updated")
    assert compute_embedding_content_hash("openai", "m", base) != compute_embedding_content_hash(
        "openai", "m", changed
    )


def test_model_change_changes_hash() -> None:
    text = build_canonical_embedding_text("A", "B")
    assert compute_embedding_content_hash("openai", "model-a", text) != compute_embedding_content_hash(
        "openai", "model-b", text
    )
