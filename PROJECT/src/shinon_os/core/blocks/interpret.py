from __future__ import annotations

from shinon_os.core import intents
from shinon_os.core.types import Intent


def parse_input(raw_text: str, current_view: str) -> Intent:
    text = raw_text.strip()
    low = text.lower()

    if not text:
        return Intent(kind=intents.HELP, raw=raw_text)
    if low in {"q", "quit", "exit"}:
        return Intent(kind=intents.QUIT, raw=raw_text)
    if low in {"h", "help", "?"}:
        return Intent(kind=intents.HELP, raw=raw_text)
    if low in {"dashboard", "dash", "d"}:
        return Intent(kind=intents.VIEW_DASH, raw=raw_text)
    if low in {"market", "m"}:
        return Intent(kind=intents.VIEW_MARKET, raw=raw_text)
    if low in {"policies", "policy", "p"}:
        return Intent(kind=intents.VIEW_POLICIES, raw=raw_text)
    if low in {"industry", "i"}:
        return Intent(kind=intents.VIEW_INDUSTRY, raw=raw_text)
    if low in {"history", "hist"}:
        return Intent(kind=intents.VIEW_HISTORY, raw=raw_text)
    if low.startswith("explain"):
        topic = text[7:].strip() if len(text) > 7 else ""
        return Intent(kind=intents.EXPLAIN, raw=raw_text, args={"topic": topic or "general"})

    if low.startswith("enact ") or low.startswith("apply "):
        tokens = text.split()
        if len(tokens) < 2:
            return Intent(kind=intents.ENACT_POLICY, raw=raw_text, args={"invalid": "missing policy_id"})
        policy_id = tokens[1].upper()
        magnitude = None
        target = None
        if len(tokens) >= 3:
            try:
                magnitude = float(tokens[2])
            except ValueError:
                return Intent(
                    kind=intents.ENACT_POLICY,
                    raw=raw_text,
                    args={"policy_id": policy_id, "invalid": "magnitude is not numeric"},
                )
        if len(tokens) >= 4:
            target = tokens[3].lower()
        return Intent(
            kind=intents.ENACT_POLICY,
            raw=raw_text,
            args={"policy_id": policy_id, "magnitude": magnitude, "target": target},
        )

    return Intent(kind=intents.HELP, raw=raw_text, args={"unknown_command": text, "view": current_view})
