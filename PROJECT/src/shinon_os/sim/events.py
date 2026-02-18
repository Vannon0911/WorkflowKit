from __future__ import annotations

from typing import Any

from shinon_os.sim.model import MarketGood, SectorState, WorldState
from shinon_os.sim.worldgen import EventDefinition
from shinon_os.util.rng import seeded_rng


def _conditions_match(event: EventDefinition, world: WorldState, market: dict[str, MarketGood]) -> bool:
    conditions = event.conditions
    world_min = conditions.get("world_min", {})
    world_max = conditions.get("world_max", {})
    good_price_min = conditions.get("good_price_min", {})
    good_price_max = conditions.get("good_price_max", {})

    for key, value in world_min.items():
        if float(getattr(world, key)) < float(value):
            return False
    for key, value in world_max.items():
        if float(getattr(world, key)) > float(value):
            return False
    for good_id, value in good_price_min.items():
        if good_id not in market or market[good_id].price < float(value):
            return False
    for good_id, value in good_price_max.items():
        if good_id not in market or market[good_id].price > float(value):
            return False
    return True


def choose_event(
    events: list[EventDefinition],
    world: WorldState,
    market: dict[str, MarketGood],
    seed: int,
    turn: int,
    event_chance: float,
) -> EventDefinition | None:
    rng = seeded_rng(seed, "event", turn)
    if rng.random() > event_chance:
        return None

    candidates: list[tuple[EventDefinition, float]] = []
    for event in events:
        if _conditions_match(event, world, market):
            candidates.append((event, max(0.0, float(event.base_weight))))
    total = sum(weight for _, weight in candidates)
    if total <= 0:
        return None

    pick = rng.uniform(0.0, total)
    cursor = 0.0
    for event, weight in candidates:
        cursor += weight
        if pick <= cursor:
            return event
    return candidates[-1][0] if candidates else None


def apply_event(
    event: EventDefinition,
    world: WorldState,
    market: dict[str, MarketGood],
    sectors: dict[str, SectorState],
) -> dict[str, Any]:
    effects = event.effects

    for key, value in effects.get("world_add", {}).items():
        if key == "treasury":
            current = int(world.treasury)
            world.treasury = int(round(current + float(value)))
        else:
            current = float(getattr(world, key))
            setattr(world, key, current + float(value))

    for good_id, value in effects.get("good_supply_mult", {}).items():
        if good_id in market:
            market[good_id].supply *= max(0.05, 1.0 + float(value))
    for good_id, value in effects.get("good_demand_mult", {}).items():
        if good_id in market:
            market[good_id].demand *= max(0.05, 1.0 + float(value))
    for good_id, value in effects.get("good_price_mult", {}).items():
        if good_id in market:
            market[good_id].price *= max(0.05, 1.0 + float(value))

    for sector_id, value in effects.get("sector_efficiency_mult", {}).items():
        if sector_id in sectors:
            sectors[sector_id].efficiency *= max(0.05, 1.0 + float(value))

    return {
        "id": event.event_id,
        "label": event.label,
        "description": event.description,
    }
