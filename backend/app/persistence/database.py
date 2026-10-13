from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.persistence import models  # noqa: F401 — register metadata
from app.persistence.base import Base

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def reset_database() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def init_database(database_url: str) -> None:
    global _engine, _session_factory
    if _engine is None:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        pool_kwargs = {}
        if database_url in {"sqlite:///:memory:", "sqlite://"}:
            pool_kwargs["poolclass"] = StaticPool
        _engine = create_engine(database_url, connect_args=connect_args, **pool_kwargs)
        _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=_engine)
    with _engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database has not been initialized")
    return _engine


def get_db_session() -> Generator[Session, None, None]:
    if _session_factory is None:
        raise RuntimeError("Database has not been initialized")
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
