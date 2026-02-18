from __future__ import annotations

import json
from pathlib import Path

import pytest

from shinon_os.app import run_app
from shinon_os.ui import factory as ui_factory


class _BrokenSession:
    def run(self, service):  # pragma: no cover - exercised via raised exception
        raise RuntimeError("forced session crash")


def test_transcript_written_on_session_error(monkeypatch, tmp_path: Path) -> None:
    local_app = tmp_path / "localapp"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app))
    monkeypatch.setattr(ui_factory, "create_ui", lambda service: _BrokenSession())

    with pytest.raises(RuntimeError, match="forced session crash"):
        run_app(ui_mode="plain", no_anim=True, safe_ui=True)

    transcript_dir = local_app / "shinon_os" / "docs" / "transcripts"
    json_files = sorted(transcript_dir.glob("session_*.json"))
    assert json_files

    payload = json.loads(json_files[-1].read_text(encoding="utf-8"))
    assert payload["status"] == "error"
    assert "forced session crash" in (payload["error"] or "")
