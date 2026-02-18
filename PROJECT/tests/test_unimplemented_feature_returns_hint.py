from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService


def test_unimplemented_feature_returns_hint(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "hint.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    service.app.start_new_game(seed=202)
    resp = service.handle_input("please launch a satellite now")
    assert resp.turn_advanced is False
    assert "Subsystem not available" in resp.message
    service.shutdown()
