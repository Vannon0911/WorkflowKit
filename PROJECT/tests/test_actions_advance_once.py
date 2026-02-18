from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_action_advances_exactly_once(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "actions.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=99)
        start_turn = app.current_turn()
        response = app.process_command("enact TAX_ADJUST 0.05")
        assert response.turn_advanced is True
        assert app.current_turn() == start_turn + 1

        view_response = app.process_command("dashboard")
        assert view_response.turn_advanced is False
        assert app.current_turn() == start_turn + 1
    finally:
        app.shutdown()
