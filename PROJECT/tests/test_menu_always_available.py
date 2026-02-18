from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService


def test_menu_always_available(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "menu.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    menu = service.get_menu()
    assert menu.commands
    assert menu.hotkeys
    service.shutdown()
