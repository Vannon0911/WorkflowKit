from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def run_sequence(db_path: Path, log_dir: Path, seed: int) -> dict[str, object]:
    app = ShinonApp(db_path=db_path, log_dir=log_dir)
    try:
        app.start_new_game(seed=seed)
        commands = [
            "enact SUBSIDY_SECTOR 1.0 agriculture",
            "enact IMPORT_PROGRAM 10 grain",
            "market",
            "enact FUND_RESEARCH 1.0",
            "enact SECURITY_BUDGET 1.0",
        ]
        for cmd in commands:
            response = app.process_command(cmd)
            if cmd.startswith("enact"):
                assert response.turn_advanced is True
                assert "INVALID PARAM" not in response.output
        return app.snapshot()
    finally:
        app.shutdown()


def test_determinism(tmp_path: Path) -> None:
    seed = 777
    left = run_sequence(tmp_path / "left.sqlite3", tmp_path / "logs_left", seed=seed)
    right = run_sequence(tmp_path / "right.sqlite3", tmp_path / "logs_right", seed=seed)
    assert left == right
