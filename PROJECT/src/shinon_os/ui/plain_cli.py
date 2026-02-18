from __future__ import annotations

from shinon_os.app import select_profile
from shinon_os.app_service import AppService
from shinon_os.cli.io import print_block, safe_input


class PlainCliSession:
    def run(self, service: AppService) -> int:
        try:
            print_block("SHINON // fixed boot sequence")
            boot = service.bootstrap()
            print_block(boot.message)
            select_profile(service.app, ask_input=safe_input, emit=print_block)

            print_block("SHINON // chat console active")
            first = service.handle_input("show dashboard status")
            print_block(first.message)
            while True:
                raw = safe_input("operator> ")
                response = service.handle_input(raw)
                print_block(response.message)
                if response.should_quit:
                    service.finalize_transcript_ok()
                    return 0
        except Exception as exc:
            service.finalize_transcript_error(exc)
            raise
