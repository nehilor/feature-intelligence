from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def init_database(database_url: str) -> None:
    global _engine, _session_factory
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    _engine = create_engine(database_url, connect_args=connect_args)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
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
