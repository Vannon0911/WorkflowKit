from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_fresh_system_persists_state_across_restarts(monkeypatch, tmp_path: Path) -> None:
    local_app = tmp_path / "localapp"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app))

    app1 = ShinonApp()
    try:
        assert app1.db_path == local_app / "shinon_os" / "shinon.sqlite3"
        assert not app1.has_existing_game()
        app1.start_new_game(seed=42)
    finally:
        app1.shutdown()

    app2 = ShinonApp()
    try:
        assert app2.has_existing_game()
        app2.load_game()
        assert app2.current_turn() == 0
    finally:
        app2.shutdown()
