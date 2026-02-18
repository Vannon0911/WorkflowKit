from __future__ import annotations

import hashlib
import random


def stable_seed(base_seed: int, *parts: object) -> int:
    raw = "|".join([str(base_seed), *[str(p) for p in parts]]).encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def seeded_rng(base_seed: int, *parts: object) -> random.Random:
    return random.Random(stable_seed(base_seed, *parts))


def bounded_noise(base_seed: int, turn: int, key: str, amplitude: float = 0.01) -> float:
    return seeded_rng(base_seed, "noise", turn, key).uniform(-amplitude, amplitude)
