from __future__ import annotations

import argparse

from shinon_os.app import run_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="shinon_os")
    parser.add_argument("--ui", choices=["textual", "plain"], default=None)
    parser.add_argument("--no-anim", action="store_true", help="Disable boot/idle animations")
    parser.add_argument("--safe-ui", action="store_true", help="Force plain fallback UI")
    args = parser.parse_args()
    run_app(ui_mode=args.ui, no_anim=args.no_anim, safe_ui=args.safe_ui)


if __name__ == "__main__":
    main()
