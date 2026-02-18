from __future__ import annotations

import re

from shinon_os.core import intents
from shinon_os.core.types import Intent


def _extract_number(text: str) -> float | None:
    match = re.search(r"(-?\d+(?:[.,]\d+)?)", text)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def _extract_target(text: str, candidates: set[str]) -> str | None:
    for candidate in sorted(candidates):
        if re.search(rf"\b{re.escape(candidate)}\b", text):
            return candidate
    return None


def _policy_hint(text: str) -> tuple[str | None, float]:
    rules = [
        ("FUND_RESEARCH", ["research", "forschung", "innovation", "tech"], 0.88),
        ("SECURITY_BUDGET", ["security", "police", "sicherheit"], 0.86),
        ("RATIONING", ["ration", "rationing", "rationierung"], 0.84),
        ("IMPORT_PROGRAM", ["import", "imports"], 0.85),
        ("BUILD_INFRA", ["infra", "infrastructure", "infrastruktur", "build"], 0.82),
        ("SUBSIDY_SECTOR", ["subsidy", "subsidize", "foerder", "support sector"], 0.82),
        ("WORK_HOURS_REFORM", ["work hours", "arbeitszeit", "labor reform"], 0.8),
        ("TAX_ADJUST", ["tax", "steuer"], 0.83),
    ]
    for policy_id, words, confidence in rules:
        if any(word in text for word in words):
            return policy_id, confidence
    return None, 0.0


def parse_input(raw_text: str, current_view: str, policy_target_types: dict[str, str] | None = None) -> Intent:
    text = raw_text.strip()
    low = text.lower()
    target_types = policy_target_types or {}
    sector_candidates = {"agriculture", "industry", "services"}
    good_candidates = {"grain", "bread", "wood", "tools", "ore", "metal", "medicine", "fuel"}

    if not text:
        return Intent(kind=intents.HELP, raw=raw_text, confidence=1.0)
    if low in {"q", "quit", "exit"}:
        return Intent(kind=intents.QUIT, raw=raw_text, confidence=1.0)
    if low in {"h", "help", "?"}:
        return Intent(kind=intents.HELP, raw=raw_text, confidence=1.0)
    if low in {"dashboard", "dash", "d"}:
        return Intent(kind=intents.VIEW_DASH, raw=raw_text, confidence=1.0)
    if low in {"market", "m"}:
        return Intent(kind=intents.VIEW_MARKET, raw=raw_text, confidence=1.0)
    if low in {"policies", "policy", "p"}:
        return Intent(kind=intents.VIEW_POLICIES, raw=raw_text, confidence=1.0)
    if low in {"industry", "i"}:
        return Intent(kind=intents.VIEW_INDUSTRY, raw=raw_text, confidence=1.0)
    if low in {"history", "hist"}:
        return Intent(kind=intents.VIEW_HISTORY, raw=raw_text, confidence=1.0)
    if low.startswith("explain"):
        topic = text[7:].strip() if len(text) > 7 else ""
        return Intent(kind=intents.EXPLAIN, raw=raw_text, args={"topic": topic or "general"}, confidence=1.0)

    if low.startswith("enact ") or low.startswith("apply "):
        tokens = text.split()
        if len(tokens) < 2:
            return Intent(kind=intents.ENACT_POLICY, raw=raw_text, args={"invalid": "missing policy_id"}, confidence=1.0)
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
                    confidence=1.0,
                )
        if len(tokens) >= 4:
            target = tokens[3].lower()
        missing: list[str] = []
        target_type = target_types.get(policy_id, "none")
        if target_type in {"sector", "good"} and not target:
            missing.append("target")
        return Intent(
            kind=intents.ENACT_POLICY,
            raw=raw_text,
            args={"policy_id": policy_id, "magnitude": magnitude, "target": target},
            confidence=1.0,
            auto_execute=len(missing) == 0,
            missing_params=missing,
        )

    if any(view_word in low for view_word in ["zeige", "show", "status", "lage", "dashboard", "markt", "market", "history"]):
        if "market" in low or "markt" in low or "price" in low:
            return Intent(kind=intents.VIEW_MARKET, raw=raw_text, confidence=0.78)
        if "history" in low:
            return Intent(kind=intents.VIEW_HISTORY, raw=raw_text, confidence=0.78)
        if "industry" in low or "sektor" in low:
            return Intent(kind=intents.VIEW_INDUSTRY, raw=raw_text, confidence=0.75)
        return Intent(kind=intents.VIEW_DASH, raw=raw_text, confidence=0.76)

    policy_id, confidence = _policy_hint(low)
    if policy_id:
        magnitude = _extract_number(low)
        target = None
        missing: list[str] = []
        target_type = target_types.get(policy_id, "none")
        if target_type == "sector":
            target = _extract_target(low, sector_candidates)
            if target is None:
                missing.append("target")
        elif target_type == "good":
            target = _extract_target(low, good_candidates)
            if target is None:
                missing.append("target")
        auto_execute = confidence >= 0.8 and not missing
        return Intent(
            kind=intents.ENACT_POLICY,
            raw=raw_text,
            args={"policy_id": policy_id, "magnitude": magnitude, "target": target},
            confidence=confidence,
            auto_execute=auto_execute,
            missing_params=missing,
        )

    return Intent(
        kind=intents.HELP,
        raw=raw_text,
        args={"unknown_command": text, "view": current_view},
        confidence=0.2,
    )
