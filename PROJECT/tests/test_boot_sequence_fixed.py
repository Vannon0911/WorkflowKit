from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def test_boot_sequence_fixed(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "boot.sqlite3", log_dir=tmp_path / "logs")
    try:
        model = app.boot_sequence_model()
        assert model.status == "PENDING"
        assert model.stages == [
            "Kernel init",
            "DB mount / migration check",
            "Subsystem checks",
            "SHINON online",
        ]
        assert 2000 <= sum(model.durations_ms) <= 4000

        lines: list[str] = []
        app.run_boot_sequence(emit=lines.append, sleep_fn=lambda _: None)
        assert lines[0].startswith("[BOOT] Kernel init")
        assert lines[-1] == "[BOOT] SHINON kernel ready."
        assert app.boot_sequence_model().status == "DONE"
    finally:
        app.shutdown()
