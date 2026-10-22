from flask import Flask

from .config import Settings, load_settings
from .instance_lock import SingleInstanceLock, lock_path_for_database


def create_app(settings: Settings | None = None) -> Flask:
    resolved_settings = load_settings() if settings is None else settings
    instance_lock: SingleInstanceLock | None = None
    if resolved_settings.environment == "production":
        instance_lock = SingleInstanceLock(lock_path_for_database(resolved_settings.duckdb_path))
        instance_lock.acquire()

    try:
        app = Flask(__name__)
        app.config.from_mapping(resolved_settings.as_flask_config())

        @app.get("/api/health/live")
        def live() -> tuple[dict[str, str], int]:
            return {"status": "ok"}, 200
    except BaseException:
        if instance_lock is not None:
            instance_lock.release()
        raise

    if instance_lock is not None:
        app.extensions["single_instance_lock"] = instance_lock
    return app
