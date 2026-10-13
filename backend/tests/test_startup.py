import os

from app.core.config import get_settings
from app.main import create_app
from fastapi.testclient import TestClient


def test_startup_without_ai_credentials():
    for key in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
        os.environ.pop(key, None)
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    get_settings.cache_clear()
    application = create_app()
    with TestClient(application) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
    get_settings.cache_clear()


def test_uses_isolated_database_not_dev_file(tmp_path, monkeypatch):
    dev_db = tmp_path / "dev_should_not_be_used.db"
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    get_settings.cache_clear()
    application = create_app()
    with TestClient(application) as client:
        assert client.get("/api/health").status_code == 200
    assert not dev_db.exists()
    get_settings.cache_clear()
