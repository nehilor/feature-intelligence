import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure tests never use developer AI keys or default dev database.
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.core.config import get_settings
from app.main import create_app
from app.persistence.database import init_database, reset_database


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Generator[None, None, None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    reset_database()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    get_settings.cache_clear()
    reset_database()
    init_database(os.environ["DATABASE_URL"])
    application = create_app()
    with TestClient(application) as test_client:
        yield test_client
    reset_database()
