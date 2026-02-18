from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService


def test_command_compatibility_view_no_turn(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "cmd.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    service.app.start_new_game(seed=99)
    turn_before = service.app.current_turn()
    resp = service.handle_input("show market prices")
    assert resp.turn_advanced is False
    assert service.app.current_turn() == turn_before
    assert resp.view_model is not None
    service.shutdown()


def test_command_compatibility_action_advances(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "cmd2.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    service.app.start_new_game(seed=101)
    turn_before = service.app.current_turn()
    resp = service.handle_input("Please fund research by 1.0 now")
    assert resp.turn_advanced is True
    assert service.app.current_turn() == turn_before + 1
    service.shutdown()
