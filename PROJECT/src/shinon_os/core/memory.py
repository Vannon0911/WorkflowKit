from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class KernelMemory:
    limit: int = 12
    entries: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=12))

    def record(self, payload: dict[str, Any]) -> None:
        self.entries.append(payload)

    def latest(self, count: int = 5) -> list[dict[str, Any]]:
        return list(self.entries)[-count:]
