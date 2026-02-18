from __future__ import annotations

from shinon_os.app import select_profile
from shinon_os.app_service import AppService
from shinon_os.cli.io import print_block, safe_input
from shinon_os.i18n import t


class PlainCliSession:
    def run(self, service: AppService) -> int:
        print_block(t("plain.boot.title"))
        boot = service.bootstrap()
        print_block(boot.message)
        select_profile(service.app, ask_input=safe_input, emit=print_block)

        print_block(t("plain.console.active"))
        first = service.handle_input("show dashboard status")
        print_block(first.message)
        while True:
            raw = safe_input(t("plain.prompt.operator"))
            response = service.handle_input(raw)
            print_block(response.message)
            if response.should_quit:
                return 0
