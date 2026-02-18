from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService
from shinon_os.ui import factory
from shinon_os.ui.plain_cli import PlainCliSession
from shinon_os.ui.textual_app import TextualSession


def test_default_prefers_fullscreen_textual(monkeypatch, tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "noscreen_default.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    monkeypatch.setattr(factory, "textual_available", lambda: True)
    ui = factory.create_ui(service)
    assert isinstance(ui, TextualSession)


def test_plain_only_when_forced(monkeypatch, tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "noscreen_plain.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(ui_mode="plain", no_anim=True), app=app)
    monkeypatch.setattr(factory, "textual_available", lambda: True)
    ui = factory.create_ui(service)
    assert isinstance(ui, PlainCliSession)
