import os
import re
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DUCKDB_FEASIBILITY_PATH = (
    PROJECT_ROOT / ".agents" / "tasks" / "online_chat" / "duckdb-feasibility.md"
)


class DuckDBFeasibilityError(ValueError):
    """Raised when the approved DuckDB feasibility gate does not allow startup."""


def validate_duckdb_feasibility(path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DuckDBFeasibilityError(f"DuckDB feasibility gate is unavailable: {path}") from exc

    lines = content.splitlines()
    try:
        conclusion_index = next(
            index for index, line in enumerate(lines) if line.strip() == "## 结论"
        )
    except StopIteration as exc:
        raise DuckDBFeasibilityError(
            'DuckDB feasibility gate must contain a "## 结论" section.'
        ) from exc

    conclusion = next(
        (line.strip() for line in lines[conclusion_index + 1 :] if line.strip()), None
    )
    if conclusion is None or re.fullmatch(r"\*\*满足\*\*[。.]?", conclusion) is None:
        raise DuckDBFeasibilityError(
            'DuckDB feasibility gate must have the exact conclusion "满足".'
        )


@dataclass(frozen=True)
class Settings:
    duckdb_path: Path
    workers: int = 1
    environment: str = "development"
    duckdb_feasibility_path: Path = field(default=DEFAULT_DUCKDB_FEASIBILITY_PATH)

    def __post_init__(self) -> None:
        if self.workers != 1:
            raise ValueError("Only one application worker may write the shared DuckDB file.")
        validate_duckdb_feasibility(self.duckdb_feasibility_path)

    def as_flask_config(self) -> dict[str, object]:
        return {
            "DUCKDB_PATH": str(self.duckdb_path),
            "APP_WORKERS": self.workers,
            "ENVIRONMENT": self.environment,
            "DUCKDB_FEASIBILITY_PATH": str(self.duckdb_feasibility_path),
        }


def load_settings() -> Settings:
    workers = int(os.environ.get("APP_WORKERS", "1"))
    return Settings(
        duckdb_path=Path(os.environ.get("DUCKDB_PATH", "./data/online-chat.duckdb")),
        workers=workers,
        environment=os.environ.get("APP_ENV", "development"),
        duckdb_feasibility_path=Path(
            os.environ.get("DUCKDB_FEASIBILITY_PATH", str(DEFAULT_DUCKDB_FEASIBILITY_PATH))
        ),
    )
