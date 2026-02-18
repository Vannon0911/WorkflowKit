from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Intent:
    kind: str
    raw: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class StanceState:
    control: float = 0.34
    growth: float = 0.33
    survival: float = 0.33
    urgency: float = 0.25
    confidence: float = 0.65
    trust_in_operator: float = 0.55


@dataclass
class Plan:
    acts: list[str]
    status_line: str
    recommendations: list[str]
    predicted_impact: str
    options: list[str]


@dataclass
class KernelResponse:
    output: str
    current_view: str
    turn_advanced: bool
    should_quit: bool = False
