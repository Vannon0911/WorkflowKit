from __future__ import annotations

from shinon_os.i18n import t
from shinon_os.util.rng import seeded_rng

PHRASE_KEYS: dict[str, list[str]] = {
    "CONTROL": [
        "phrase.control.1",
        "phrase.control.2",
        "phrase.control.3",
    ],
    "GROWTH": [
        "phrase.growth.1",
        "phrase.growth.2",
        "phrase.growth.3",
    ],
    "SURVIVAL": [
        "phrase.survival.1",
        "phrase.survival.2",
        "phrase.survival.3",
    ],
}


def pick_phrase(seed: int, turn: int, stance_mode: str) -> str:
    options = PHRASE_KEYS.get(stance_mode, PHRASE_KEYS["CONTROL"])
    rng = seeded_rng(seed, "phrase", turn, stance_mode)
    return t(rng.choice(options))
