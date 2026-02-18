from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldState:
    turn: int
    treasury: int
    population: int
    prosperity: float
    stability: float
    unrest: float
    tech_level: float
    last_action_ts: str


@dataclass
class MarketGood:
    good_id: str
    supply: float
    demand: float
    price: float
    last_price: float


@dataclass
class SectorState:
    sector_id: str
    capacity: float
    efficiency: float
    upkeep: float
    inputs: dict[str, float] = field(default_factory=dict)
    outputs: dict[str, float] = field(default_factory=dict)


@dataclass
class PolicyRuntime:
    policy_id: str
    remaining_ticks: int
    cooldown_ticks: int
    magnitude: float
    state: dict[str, Any] = field(default_factory=dict)


@dataclass
class GameState:
    world: WorldState
    market: dict[str, MarketGood]
    sectors: dict[str, SectorState]
    unlocked_policies: set[str] = field(default_factory=set)
    active_policies: dict[str, PolicyRuntime] = field(default_factory=dict)


@dataclass
class SimResult:
    ok: bool
    message: str
    turn_advanced: bool
    action_label: str
    world_before: WorldState
    world_after: WorldState
    top_price_movers: list[tuple[str, float]]
    shortages: list[str]
    inflation: float
    volatility: float
    events: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
