from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


@dataclass
class SessionTranscriptWriter:
    transcript_dir: Path
    session_id: str = field(default_factory=lambda: uuid4().hex[:8])
    started_at: str | None = None
    finished_at: str | None = None
    status: str = "running"
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    entries: list[dict[str, Any]] = field(default_factory=list)
    _flushed: bool = False
    _json_path: Path | None = None
    _txt_path: Path | None = None

    def mark_started(self, **metadata: Any) -> None:
        if self.started_at is None:
            self.started_at = _now_utc_iso()
        if metadata:
            self.metadata.update(metadata)

    def add_entry(self, role: str, text: str, meta: dict[str, Any] | None = None) -> None:
        self.entries.append(
            {
                "ts": _now_utc_iso(),
                "role": role,
                "text": _safe_text(text),
                "meta": meta or {},
            }
        )

    def mark_finished(self, status: str, error: str | None = None) -> None:
        if self.finished_at is None:
            self.finished_at = _now_utc_iso()
        self.status = status
        self.error = _safe_text(error) if error else None

    def _ensure_paths(self) -> tuple[Path, Path]:
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        if self._json_path and self._txt_path:
            return self._json_path, self._txt_path
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"session_{stamp}_{self.session_id}"
        self._json_path = self.transcript_dir / f"{base}.json"
        self._txt_path = self.transcript_dir / f"{base}.txt"
        return self._json_path, self._txt_path

    def flush(self) -> tuple[Path, Path]:
        json_path, txt_path = self._ensure_paths()
        payload = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "error": self.error,
            "metadata": self.metadata,
            "entries": self.entries,
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

        lines = [
            f"session_id: {self.session_id}",
            f"started_at: {self.started_at or ''}",
            f"finished_at: {self.finished_at or ''}",
            f"status: {self.status}",
            f"error: {self.error or ''}",
            "",
            "entries:",
        ]
        for entry in self.entries:
            lines.append(f"[{entry['ts']}] {entry['role']}: {entry['text']}")
            if entry["meta"]:
                lines.append(f"  meta: {json.dumps(entry['meta'], ensure_ascii=True)}")
        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self._flushed = True
        return json_path, txt_path
