from flask import Flask

from . import create_app
from .config import Settings, load_settings
from .instance_lock import SingleInstanceLock, lock_path_for_database

__all__ = ["SingleInstanceLock", "create_production_app", "lock_path_for_database"]


def create_production_app(settings: Settings | None = None) -> Flask:
    resolved_settings = load_settings() if settings is None else settings
    if resolved_settings.environment != "production":
        raise RuntimeError("Production WSGI entry requires APP_ENV=production.")

    return create_app(resolved_settings)
