from __future__ import annotations

from shinon_os.util.rng import seeded_rng

PHRASES: dict[str, list[str]] = {
    "CONTROL": [
        "Signal noisy. Prioritize stability containment.",
        "Unrest envelope widening. Control posture recommended.",
        "Order maintenance beats speculative growth in this window.",
    ],
    "GROWTH": [
        "System stable enough for targeted expansion.",
        "Growth vector viable if treasury risk remains bounded.",
        "Productivity runway open. Use it before volatility widens.",
    ],
    "SURVIVAL": [
        "Liquidity and shortages are primary constraints.",
        "Treasury buffer thin. Preserve operational continuity.",
        "Risk floor breached. Defensive allocation required.",
    ],
}


def pick_phrase(seed: int, turn: int, stance_mode: str) -> str:
    options = PHRASES.get(stance_mode, PHRASES["CONTROL"])
    rng = seeded_rng(seed, "phrase", turn, stance_mode)
    return rng.choice(options)
