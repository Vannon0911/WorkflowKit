from __future__ import annotations

from shinon_os.sim.model import MarketGood


def compute_derived_metrics(
    before: dict[str, MarketGood],
    after: dict[str, MarketGood],
    shortage_threshold: float,
) -> dict[str, object]:
    shortages: list[str] = []
    deltas: list[tuple[str, float]] = []
    inflation_terms: list[float] = []
    volatility_terms: list[float] = []

    for good_id, now in after.items():
        prev = before[good_id]
        if now.supply < now.demand * (1.0 - shortage_threshold):
            shortages.append(good_id)
        if prev.price > 0:
            delta = (now.price - prev.price) / prev.price
            deltas.append((good_id, delta * 100.0))
            inflation_terms.append(delta)
            volatility_terms.append(abs(delta))

    inflation = (sum(inflation_terms) / len(inflation_terms) * 100.0) if inflation_terms else 0.0
    volatility = (sum(volatility_terms) / len(volatility_terms) * 100.0) if volatility_terms else 0.0
    top_movers = sorted(deltas, key=lambda item: abs(item[1]), reverse=True)[:3]

    return {
        "shortages": shortages,
        "inflation": inflation,
        "volatility": volatility,
        "top_movers": top_movers,
    }
