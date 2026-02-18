from __future__ import annotations

import os
from importlib import resources
from pathlib import Path


def user_data_dir(app_name: str = "shinon_os") -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base = Path(local_app_data)
    else:
        base = Path.home() / ".local" / "share"
    path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_db_path() -> Path:
    return user_data_dir() / "shinon.sqlite3"


def default_log_dir() -> Path:
    path = user_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_docs_dir() -> Path:
    path = user_data_dir() / "docs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def package_data_dir() -> Path:
    return Path(str(resources.files("shinon_os.data")))
