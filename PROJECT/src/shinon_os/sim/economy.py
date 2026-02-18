from __future__ import annotations

from typing import Any

from shinon_os.sim.model import MarketGood, SectorState, WorldState
from shinon_os.util.rng import bounded_noise


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def simulate_market(
    world: WorldState,
    market: dict[str, MarketGood],
    sectors: dict[str, SectorState],
    goods_meta: dict[str, dict[str, Any]],
    economy_cfg: dict[str, Any],
    population_needs: dict[str, float],
    effects: dict[str, Any],
    seed: int,
    turn: int,
) -> dict[str, MarketGood]:
    k_demand = float(economy_cfg.get("k_demand", 0.35))
    noise_amplitude = float(economy_cfg.get("noise_amplitude", 0.01))
    eps = 1e-6

    updated: dict[str, MarketGood] = {}
    for good_id, current in market.items():
        updated[good_id] = MarketGood(
            good_id=good_id,
            supply=max(current.supply * 0.45, 0.1),
            demand=max(current.demand * 0.45, 0.1),
            price=current.price,
            last_price=current.price,
        )

    global_output_mult = float(effects.get("global_output_mult", 0.0))
    for sector_id, sector in sectors.items():
        sector_eff_add = float(effects.get("sector_efficiency_add", {}).get(sector_id, 0.0))
        sector_output_add = float(effects.get("sector_output_mult", {}).get(sector_id, 0.0))
        throughput = sector.capacity * clamp(sector.efficiency + sector_eff_add, 0.05, 1.5)
        throughput *= max(0.2, 1.0 + global_output_mult)
        output_factor = max(0.2, 1.0 + sector_output_add)

        for good_id, amount in sector.inputs.items():
            if good_id in updated:
                updated[good_id].demand += throughput * float(amount)
        for good_id, amount in sector.outputs.items():
            if good_id in updated:
                updated[good_id].supply += throughput * float(amount) * output_factor

    living_factor = 0.8 + world.prosperity / 200.0
    for good_id, base_need in population_needs.items():
        if good_id in updated:
            updated[good_id].demand += world.population * float(base_need) * living_factor

    for good_id, amount in effects.get("good_supply_add", {}).items():
        if good_id in updated:
            updated[good_id].supply += float(amount)

    for good_id, multiplier_add in effects.get("good_demand_mult", {}).items():
        if good_id in updated:
            updated[good_id].demand *= max(0.1, 1.0 + float(multiplier_add))

    for good_id, item in updated.items():
        prev_price = market[good_id].price
        ratio = item.demand / max(item.supply, eps)
        target = clamp(ratio, 0.5, 2.0)
        trend = lerp(1.0, target, k_demand)
        noise = bounded_noise(seed, turn, good_id, amplitude=noise_amplitude)
        price = prev_price * trend * (1.0 + noise)
        event_price_add = float(effects.get("good_price_mult", {}).get(good_id, 0.0))
        price *= max(0.1, 1.0 + event_price_add)
        meta = goods_meta[good_id]
        item.price = clamp(price, float(meta["min_price"]), float(meta["max_price"]))

    return updated
