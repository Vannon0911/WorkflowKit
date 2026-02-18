from __future__ import annotations

from shinon_os.sim.model import GameState, WorldState


def build_observations(state: GameState, last_world_snapshot: WorldState | None) -> dict[str, object]:
    shortages = [
        good_id
        for good_id, item in state.market.items()
        if item.supply < item.demand * 0.88
    ]

    deltas = []
    for item in state.market.values():
        if item.last_price > 0:
            deltas.append((item.price - item.last_price) / item.last_price)
    inflation = (sum(deltas) / len(deltas) * 100.0) if deltas else 0.0
    volatility = (sum(abs(delta) for delta in deltas) / len(deltas) * 100.0) if deltas else 0.0

    unrest_trend = 0.0
    treasury_trend = 0.0
    if last_world_snapshot is not None:
        unrest_trend = state.world.unrest - last_world_snapshot.unrest
        treasury_trend = float(state.world.treasury - last_world_snapshot.treasury)

    risk_scores = {
        "shortage_risk": min(1.0, len(shortages) / 4.0),
        "fiscal_risk": min(1.0, max(0.0, (25000.0 - state.world.treasury) / 25000.0)),
        "social_risk": min(1.0, state.world.unrest / 100.0),
        "inflation_risk": min(1.0, max(0.0, inflation) / 10.0),
    }

    return {
        "shortages": shortages,
        "inflation": inflation,
        "volatility": volatility,
        "unrest_trend": unrest_trend,
        "treasury_trend": treasury_trend,
        "risk_scores": risk_scores,
    }
