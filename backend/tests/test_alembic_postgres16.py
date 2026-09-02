"""Smoke test de la cadena Alembic sobre una instancia PostgreSQL 16 vacia."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import psycopg
import pytest
from langchain_postgres import PostgresChatMessageHistory


BACKEND_ROOT = Path(__file__).resolve().parents[1]
POSTGRES_IMAGE = "postgres:16-alpine"


def _run_alembic(database_url: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def _assert_empty_postgres16(database_url: str) -> None:
    with psycopg.connect(database_url) as connection:
        assert 160000 <= connection.info.server_version < 170000
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = 'public'
                """
            )
            assert cursor.fetchall() == []


@contextmanager
def _docker_postgres16() -> Iterator[str]:
    if shutil.which("docker") is None:
        pytest.skip("Docker no esta disponible y ALEMBIC_TEST_DATABASE_URL no fue configurada")
    docker_info = subprocess.run(
        ["docker", "info"],
        check=False,
        capture_output=True,
        text=True,
    )
    if docker_info.returncode != 0:
        pytest.skip("El daemon Docker no esta disponible y ALEMBIC_TEST_DATABASE_URL no fue configurada")

    container_name = f"mga-alembic-{uuid.uuid4().hex[:12]}"
    password = uuid.uuid4().hex
    subprocess.run(
        [
            "docker", "run", "--detach", "--rm",
            "--name", container_name,
            "--env", f"POSTGRES_PASSWORD={password}",
            "--publish", "127.0.0.1::5432",
            POSTGRES_IMAGE,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        port_result = subprocess.run(
            ["docker", "port", container_name, "5432/tcp"],
            check=True,
            capture_output=True,
            text=True,
        )
        port = port_result.stdout.strip().rsplit(":", 1)[1]
        database_url = f"postgresql://postgres:{password}@127.0.0.1:{port}/postgres"

        deadline = time.monotonic() + 30
        while True:
            try:
                with psycopg.connect(database_url):
                    break
            except psycopg.OperationalError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.25)
        yield database_url
    finally:
        subprocess.run(
            ["docker", "rm", "--force", container_name],
            check=False,
            capture_output=True,
            text=True,
        )


@contextmanager
def _postgres16_database() -> Iterator[str]:
    configured_url = os.getenv("ALEMBIC_TEST_DATABASE_URL", "").strip()
    if configured_url:
        yield configured_url
        return
    with _docker_postgres16() as database_url:
        yield database_url


def test_upgrade_empty_postgres16_to_head() -> None:
    with _postgres16_database() as database_url:
        _assert_empty_postgres16(database_url)

        _run_alembic(database_url, "upgrade", "head")
        heads = _run_alembic(database_url, "heads").stdout.strip()
        current = _run_alembic(database_url, "current").stdout.strip()

        head_revision = heads.split()[0]
        assert "(head)" in heads
        assert head_revision in current
        assert "(head)" in current

        with psycopg.connect(database_url) as connection:
            PostgresChatMessageHistory.create_tables(connection, "chat_history_")

        assert "No new upgrade operations detected" in _run_alembic(
            database_url, "check"
        ).stdout

        _run_alembic(database_url, "downgrade", "-1")
        assert head_revision not in _run_alembic(database_url, "current").stdout

        _run_alembic(database_url, "upgrade", "head")
        assert head_revision in _run_alembic(database_url, "current").stdout