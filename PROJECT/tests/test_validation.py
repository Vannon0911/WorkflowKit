from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_invalid_magnitude_rejected_without_crash(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "validation.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=21)
        turn_before = app.current_turn()
        response = app.process_command("enact FUND_RESEARCH 1.3")
        assert "INVALID PARAM" in response.output
        assert response.turn_advanced is False
        assert app.current_turn() == turn_before
    finally:
        app.shutdown()
