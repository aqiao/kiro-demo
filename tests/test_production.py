import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.production import SingleInstanceLock, create_production_app, lock_path_for_database

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def production_environment(database_path: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "APP_ENV": "production",
            "APP_WORKERS": "1",
            "DUCKDB_PATH": str(database_path),
            "PYTHONPATH": os.pathsep.join(
                [str(PROJECT_ROOT), environment.get("PYTHONPATH", "")]
            ).rstrip(os.pathsep),
        }
    )
    return environment


def test_shared_database_lock_rejects_a_second_lock_in_process(tmp_path):
    database_path = tmp_path / "chat.duckdb"
    first_lock = SingleInstanceLock(lock_path_for_database(database_path))
    second_lock = SingleInstanceLock(lock_path_for_database(database_path))

    first_lock.acquire()
    try:
        with pytest.raises(RuntimeError, match="already owns"):
            second_lock.acquire()
    finally:
        first_lock.release()
        second_lock.release()


def test_create_app_rejects_a_second_independent_process(tmp_path):
    database_path = tmp_path / "chat.duckdb"
    environment = production_environment(database_path)
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "from app import create_app; import sys; app=create_app(); "
                "print('READY', flush=True); sys.stdin.read()"
            ),
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "READY"
        assert lock_path_for_database(database_path).exists()

        contender = subprocess.run(
            [sys.executable, "-c", "from app import create_app; create_app()"],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        assert contender.returncode != 0
        assert "Another application process already owns" in contender.stderr
    finally:
        if holder.stdin is not None:
            holder.stdin.close()
        holder.terminate()
        holder.wait(timeout=5)


def test_production_app_requires_production_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DUCKDB_PATH", str(tmp_path / "chat.duckdb"))

    with pytest.raises(RuntimeError, match="APP_ENV=production"):
        create_production_app()


def test_production_app_holds_the_database_lock(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_WORKERS", "1")
    monkeypatch.setenv("DUCKDB_PATH", str(tmp_path / "chat.duckdb"))

    app = create_production_app()
    try:
        assert app.config["APP_WORKERS"] == 1
        assert "single_instance_lock" in app.extensions
    finally:
        app.extensions["single_instance_lock"].release()


def test_standard_wsgi_entry_starts_with_one_worker(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import wsgi; assert wsgi.app.config['APP_WORKERS'] == 1",
        ],
        cwd=PROJECT_ROOT,
        env=production_environment(tmp_path / "chat.duckdb"),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
