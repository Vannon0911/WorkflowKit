from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_chat_ambiguous_no_execute(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "chat_amb.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=101)
        turn_before = app.current_turn()
        response = app.process_command("do something about the economy maybe")
        assert response.turn_advanced is False
        assert app.current_turn() == turn_before
        assert response.chat_turn is not None
        assert response.chat_turn.executed_action is None
    finally:
        app.shutdown()
