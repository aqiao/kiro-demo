from pathlib import Path

import pytest

from app.config import DuckDBFeasibilityError, Settings, validate_duckdb_feasibility


def write_gate(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "duckdb-feasibility.md"
    path.write_text(content, encoding="utf-8")
    return path


def test_feasibility_gate_accepts_exact_satisfied_conclusion(tmp_path):
    path = write_gate(tmp_path, "# Gate\n\n## 结论\n\n**满足**。\n")

    validate_duckdb_feasibility(path)


def test_settings_reject_missing_feasibility_gate(tmp_path):
    with pytest.raises(DuckDBFeasibilityError, match="unavailable"):
        Settings(
            duckdb_path=tmp_path / "chat.duckdb",
            duckdb_feasibility_path=tmp_path / "missing.md",
        )


def test_feasibility_gate_rejects_unsatisfied_conclusion(tmp_path):
    path = write_gate(tmp_path, "## 结论\n\n**不满足**。\n")

    with pytest.raises(DuckDBFeasibilityError, match="exact conclusion"):
        validate_duckdb_feasibility(path)


def test_feasibility_gate_rejects_invalid_format(tmp_path):
    path = write_gate(tmp_path, "## 结论\n\n本文件说明满足。\n")

    with pytest.raises(DuckDBFeasibilityError, match="exact conclusion"):
        validate_duckdb_feasibility(path)
