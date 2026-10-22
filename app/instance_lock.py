import fcntl
from pathlib import Path
from types import TracebackType
from typing import IO


class SingleInstanceLock:
    """Keep one process as the exclusive writer for a DuckDB database file."""

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self._handle: IO[str] | None = None

    def acquire(self) -> None:
        if self._handle is not None:
            return

        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            handle.close()
            raise RuntimeError(
                "Another application process already owns the shared DuckDB file."
            ) from exc
        self._handle = handle

    def release(self) -> None:
        if self._handle is None:
            return
        fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        self._handle.close()
        self._handle = None

    def __enter__(self) -> "SingleInstanceLock":
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.release()


def lock_path_for_database(database_path: Path) -> Path:
    return database_path.with_name(f"{database_path.name}.lock")
