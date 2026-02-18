from __future__ import annotations

import pytest

from shinon_os.app import ShinonApp


def test_boot_sequence_raises_on_length_mismatch(tmp_path) -> None:
    app = ShinonApp(db_path=tmp_path / "boot.sqlite3", log_dir=tmp_path / "logs")
    app._boot_model.durations_ms = [100, 200]  # fewer durations than stages
    with pytest.raises(ValueError):
        app.run_boot_sequence(emit=lambda _: None, sleep_fn=lambda *_: None)
    app.shutdown()


def test_boot_sequence_emits_all_stages(tmp_path) -> None:
    app = ShinonApp(db_path=tmp_path / "boot_ok.sqlite3", log_dir=tmp_path / "logs_ok")
    app._boot_model.durations_ms = [0] * len(app._boot_model.stages)  # fast
    emitted: list[str] = []

    app.run_boot_sequence(emit=lambda msg: emitted.append(msg), sleep_fn=lambda *_: None)

    assert len(emitted) == len(app._boot_model.stages) + 1  # stages + ready message
    assert emitted[-1].endswith("kernel ready.")
    app.shutdown()
