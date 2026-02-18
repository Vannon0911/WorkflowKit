from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

from shinon_os.util.timeutil import utc_now_iso


class JsonlRotatingLogger:
    def __init__(self, log_dir: Path, max_bytes: int = 2_000_000, backups: int = 3) -> None:
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backups = backups
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _rotate_if_needed(self, path: Path) -> None:
        if not path.exists():
            return
        if path.stat().st_size < self.max_bytes:
            return
        for idx in range(self.backups, 0, -1):
            src = path.with_suffix(path.suffix + f".{idx}")
            dst = path.with_suffix(path.suffix + f".{idx + 1}")
            if src.exists():
                if idx == self.backups:
                    src.unlink(missing_ok=True)
                else:
                    src.replace(dst)
        path.replace(path.with_suffix(path.suffix + ".1"))

    def _write(self, filename: str, payload: dict[str, Any]) -> None:
        target = self.log_dir / filename
        with self._lock:
            self._rotate_if_needed(target)
            row = {"ts": utc_now_iso(), **payload}
            with target.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=True) + os.linesep)

    def sim(self, payload: dict[str, Any]) -> None:
        self._write("sim.jsonl", payload)

    def debug(self, payload: dict[str, Any]) -> None:
        self._write("shinon_debug.jsonl", payload)

    def error(self, payload: dict[str, Any]) -> None:
        self._write("errors.jsonl", payload)
