from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_chat_intent_auto_execute(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "chat_auto.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=100)
        turn_before = app.current_turn()
        response = app.process_command("Please adjust tax by 0.05 now")
        assert response.turn_advanced is True
        assert app.current_turn() == turn_before + 1
        assert response.chat_turn is not None
        assert response.chat_turn.executed_action == "TAX_ADJUST"
    finally:
        app.shutdown()
