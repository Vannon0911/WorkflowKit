from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_chat_view_requests_no_advance(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "chat_views.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=102)
        turn_before = app.current_turn()
        for prompt in ["show market prices", "zeige dashboard", "explain prices please"]:
            response = app.process_command(prompt)
            assert response.turn_advanced is False
            assert app.current_turn() == turn_before
    finally:
        app.shutdown()
