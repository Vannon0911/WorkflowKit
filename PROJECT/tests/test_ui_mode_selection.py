from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService
from shinon_os.ui import factory
from shinon_os.ui.plain_cli import PlainCliSession
from shinon_os.ui.textual_app import TextualSession


def test_ui_defaults_to_textual_when_available(monkeypatch, tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "ui_default.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(ui_mode=None, no_anim=True, safe_ui=False), app=app)
    monkeypatch.setattr(factory, "textual_available", lambda: True)
    ui = factory.create_ui(service)
    assert isinstance(ui, TextualSession)


def test_ui_forces_plain_when_safe(monkeypatch, tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "ui_safe.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(ui_mode="textual", no_anim=True, safe_ui=True), app=app)
    monkeypatch.setattr(factory, "textual_available", lambda: True)
    ui = factory.create_ui(service)
    assert isinstance(ui, PlainCliSession)


def test_ui_plain_when_textual_unavailable(monkeypatch, tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "ui_plain.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(ui_mode="textual", no_anim=True, safe_ui=False), app=app)
    monkeypatch.setattr(factory, "textual_available", lambda: False)
    ui = factory.create_ui(service)
    assert isinstance(ui, PlainCliSession)
