"""Fixtures compartidos para pruebas de la capa de contexto semántico MGA."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
# Registra todos los modelos en Base.metadata (mismo patrón que alembic/env.py).
from app.models import *  # noqa: F401,F403


@pytest.fixture()
def db_session():
    """Sesión SQLAlchemy sobre SQLite en memoria con el esquema completo creado."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


class QueryCounter:
    """Cuenta las sentencias SQL ejecutadas por un engine mientras está activo."""

    def __init__(self, engine):
        self.engine = engine
        self.count = 0

    def __enter__(self):
        self.count = 0
        event.listen(self.engine, "before_cursor_execute", self._on_execute)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        event.remove(self.engine, "before_cursor_execute", self._on_execute)

    def _on_execute(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.fixture()
def query_counter(db_session):
    return QueryCounter(db_session.bind)
