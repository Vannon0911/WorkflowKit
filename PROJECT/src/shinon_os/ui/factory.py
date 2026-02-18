from __future__ import annotations

from shinon_os.ui.plain_cli import PlainCliSession
from shinon_os.ui.textual_app import TextualSession, textual_available


def create_ui(service):
    selected = (service.options.ui_mode or "textual").strip().lower()
    if service.options.safe_ui:
        return PlainCliSession()
    if selected == "plain":
        return PlainCliSession()
    if selected == "textual":
        if textual_available():
            return TextualSession()
        return PlainCliSession()
    return PlainCliSession()
