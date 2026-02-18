from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shinon_os.sim.model import GameState, MarketGood, SectorState, WorldState
from shinon_os.util.paths import package_data_dir
from shinon_os.util.timeutil import utc_now_iso


@dataclass(frozen=True)
class PolicyDefinition:
    policy_id: str
    label: str
    description: str
    target_type: str
    cost: int
    duration_ticks: int
    cooldown_ticks: int
    magnitude: dict[str, float]
    effects: dict[str, Any]
    constraints: dict[str, Any]


@dataclass(frozen=True)
class EventDefinition:
    event_id: str
    label: str
    description: str
    base_weight: float
    conditions: dict[str, Any]
    effects: dict[str, Any]


@dataclass(frozen=True)
class DataBundle:
    config: dict[str, Any]
    goods: list[dict[str, Any]]
    sectors: list[dict[str, Any]]
    policies: dict[str, PolicyDefinition]
    events: list[EventDefinition]

    def goods_by_id(self) -> dict[str, dict[str, Any]]:
        return {g["id"]: g for g in self.goods}

    def sector_io_defs(self) -> dict[str, dict[str, dict[str, float]]]:
        return {
            sector["id"]: {
                "inputs": dict(sector.get("inputs", {})),
                "outputs": dict(sector.get("outputs", {})),
            }
            for sector in self.sectors
        }

    def sector_ids(self) -> set[str]:
        return {s["id"] for s in self.sectors}


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _validate_data(config: dict[str, Any], goods: list[dict[str, Any]], sectors: list[dict[str, Any]], policies: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    required_world = {"population", "prosperity", "stability", "unrest", "tech_level", "treasury"}
    if not required_world.issubset(set(config.get("world", {}).keys())):
        raise ValueError("config.world is missing required keys.")

    if len(goods) != 8:
        raise ValueError("MVP requires exactly 8 goods.")
    for good in goods:
        for field in ("id", "base_supply", "base_demand", "base_price", "min_price", "max_price"):
            if field not in good:
                raise ValueError(f"Good entry missing field: {field}")

    sector_ids = {sector.get("id") for sector in sectors}
    if sector_ids != {"agriculture", "industry", "services"}:
        raise ValueError("MVP requires sectors: agriculture, industry, services.")

    if len(policies) < 8:
        raise ValueError("MVP requires at least 8 policies.")
    for policy in policies:
        for field in ("id", "label", "description", "cost", "duration_ticks", "cooldown_ticks", "magnitude", "effects", "constraints"):
            if field not in policy:
                raise ValueError(f"Policy missing field: {field}")

    if len(events) < 10:
        raise ValueError("MVP requires at least 10 event templates.")
    for event in events:
        for field in ("id", "label", "description", "base_weight", "effects"):
            if field not in event:
                raise ValueError(f"Event missing field: {field}")


def load_data(data_dir: Path | None = None) -> DataBundle:
    root = data_dir or package_data_dir()
    config = _read_json(root / "config.json")
    goods = _read_json(root / "goods.json")
    sectors = _read_json(root / "sectors.json")
    policies_raw = _read_json(root / "policies.json")
    events_raw = _read_json(root / "events.json")

    _validate_data(config, goods, sectors, policies_raw, events_raw)

    policies: dict[str, PolicyDefinition] = {}
    for row in policies_raw:
        policies[row["id"]] = PolicyDefinition(
            policy_id=row["id"],
            label=row["label"],
            description=row["description"],
            target_type=row.get("target_type", "none"),
            cost=int(row["cost"]),
            duration_ticks=int(row["duration_ticks"]),
            cooldown_ticks=int(row["cooldown_ticks"]),
            magnitude={
                "min": float(row["magnitude"]["min"]),
                "max": float(row["magnitude"]["max"]),
                "step": float(row["magnitude"]["step"]),
                "default": float(row["magnitude"]["default"]),
            },
            effects=dict(row["effects"]),
            constraints=dict(row.get("constraints", {})),
        )

    events: list[EventDefinition] = []
    for row in events_raw:
        events.append(
            EventDefinition(
                event_id=row["id"],
                label=row["label"],
                description=row["description"],
                base_weight=float(row["base_weight"]),
                conditions=dict(row.get("conditions", {})),
                effects=dict(row.get("effects", {})),
            )
        )

    return DataBundle(config=config, goods=goods, sectors=sectors, policies=policies, events=events)


def build_initial_state(bundle: DataBundle) -> GameState:
    cfg_world = bundle.config["world"]
    world = WorldState(
        turn=0,
        treasury=int(cfg_world["treasury"]),
        population=int(cfg_world["population"]),
        prosperity=float(cfg_world["prosperity"]),
        stability=float(cfg_world["stability"]),
        unrest=float(cfg_world["unrest"]),
        tech_level=float(cfg_world["tech_level"]),
        last_action_ts=utc_now_iso(),
    )

    market: dict[str, MarketGood] = {}
    for good in bundle.goods:
        market[good["id"]] = MarketGood(
            good_id=good["id"],
            supply=float(good["base_supply"]),
            demand=float(good["base_demand"]),
            price=float(good["base_price"]),
            last_price=float(good["base_price"]),
        )

    sectors: dict[str, SectorState] = {}
    for sector in bundle.sectors:
        sectors[sector["id"]] = SectorState(
            sector_id=sector["id"],
            capacity=float(sector["capacity"]),
            efficiency=float(sector["efficiency"]),
            upkeep=float(sector["upkeep"]),
            inputs=dict(sector.get("inputs", {})),
            outputs=dict(sector.get("outputs", {})),
        )

    return GameState(world=world, market=market, sectors=sectors, active_policies={})
