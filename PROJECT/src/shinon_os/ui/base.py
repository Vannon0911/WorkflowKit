from __future__ import annotations

from typing import Protocol

from shinon_os.app_service import AppService


class UISession(Protocol):
    def run(self, service: AppService) -> int: ...
