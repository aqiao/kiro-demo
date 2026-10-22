import pytest

from app.config import Settings


def test_settings_allow_only_one_worker(tmp_path):
    settings = Settings(duckdb_path=tmp_path / "chat.duckdb")

    assert settings.workers == 1
    assert settings.as_flask_config()["DUCKDB_PATH"].endswith("chat.duckdb")


def test_settings_reject_multiple_workers(tmp_path):
    with pytest.raises(ValueError, match="Only one application worker"):
        Settings(duckdb_path=tmp_path / "chat.duckdb", workers=2)
