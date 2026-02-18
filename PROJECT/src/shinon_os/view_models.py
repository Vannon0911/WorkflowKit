from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class CapabilityRegistry:
    textual_available: bool
    animations_enabled: bool
    safe_mode: bool
    palette: str = "oled"


@dataclass
class StatusModel:
    turn: int
    current_view: str
    treasury: float
    population: int
    prosperity: float
    stability: float
    unrest: float
    tech: float
    stance: dict[str, float]


@dataclass
class DashboardVM:
    shortages: list[str]
    top_movers: list[tuple[str, float]]
    active_policies: list[str]


@dataclass
class MarketRow:
    good: str
    supply: float
    demand: float
    price: float
    delta_pct: float


@dataclass
class MarketVM:
    rows: list[MarketRow]


@dataclass
class PolicyRow:
    policy_id: str
    status: str
    remaining_ticks: int
    cooldown_ticks: int
    label: str


@dataclass
class PoliciesVM:
    rows: list[PolicyRow]


@dataclass
class IndustryRow:
    sector_id: str
    capacity: float
    efficiency: float
    upkeep: float


@dataclass
class IndustryVM:
    rows: list[IndustryRow]


@dataclass
class HistoryRow:
    turn: int
    action: str
    cost: float
    inflation: float
    events: list[str]


@dataclass
class HistoryVM:
    rows: list[HistoryRow]


@dataclass
class ExplainVM:
    topic: str
    text: str


@dataclass
class MenuModel:
    commands: list[str] = field(default_factory=list)
    hotkeys: list[str] = field(default_factory=list)
    help: str = ""


@dataclass
class OSResponse:
    message: str
    view: str
    view_model: Any | None
    status: StatusModel | None
    menu: MenuModel | None
    capability: CapabilityRegistry | None
    turn_advanced: bool
    should_quit: bool = False
    locale_changed: bool = False
    events: list[str] = field(default_factory=list)
