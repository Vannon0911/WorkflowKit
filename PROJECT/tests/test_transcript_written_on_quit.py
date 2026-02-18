from __future__ import annotations

import json
from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService


def test_transcript_written_on_quit(monkeypatch, tmp_path: Path) -> None:
    local_app = tmp_path / "localapp"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app))

    app = ShinonApp(db_path=tmp_path / "quit.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(ui_mode="plain", no_anim=True, safe_ui=True), app=app)
    try:
        service.bootstrap()
        app.start_new_game(seed=42)
        response = service.handle_input("quit")
        assert response.should_quit
        service.finalize_transcript_ok()
    finally:
        service.shutdown()

    transcript_dir = local_app / "shinon_os" / "docs" / "transcripts"
    json_files = sorted(transcript_dir.glob("session_*.json"))
    txt_files = sorted(transcript_dir.glob("session_*.txt"))
    assert json_files
    assert txt_files

    payload = json.loads(json_files[-1].read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert any(entry["role"] == "user" and entry["text"] == "quit" for entry in payload["entries"])
    assert any("shutdown sequence acknowledged" in entry["text"] for entry in payload["entries"])
