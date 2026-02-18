from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_views_do_not_advance_turn(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "views.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=42)
        base_turn = app.current_turn()
        for cmd in ["dashboard", "market", "policies", "industry", "history", "explain prices"]:
            response = app.process_command(cmd)
            assert response.turn_advanced is False
            assert app.current_turn() == base_turn
    finally:
        app.shutdown()
