from __future__ import annotations

from shinon_os.core.types import StanceState


def _normalize(stance: StanceState) -> StanceState:
    total = stance.control + stance.growth + stance.survival
    if total <= 0:
        stance.control = 0.34
        stance.growth = 0.33
        stance.survival = 0.33
        return stance
    stance.control /= total
    stance.growth /= total
    stance.survival /= total
    return stance


def update_stance(observations: dict[str, object], stance: StanceState) -> StanceState:
    unrest_trend = float(observations["unrest_trend"])
    inflation = float(observations["inflation"])
    shortages = len(observations["shortages"])  # type: ignore[arg-type]
    risk_scores = observations["risk_scores"]  # type: ignore[assignment]

    stance.control *= 0.92
    stance.growth *= 0.92
    stance.survival *= 0.92

    if float(risk_scores["social_risk"]) > 0.45 or unrest_trend > 0.2:
        stance.control += 0.14
    if float(risk_scores["fiscal_risk"]) > 0.5 or shortages >= 3:
        stance.survival += 0.16
    if float(risk_scores["social_risk"]) < 0.3 and shortages <= 1:
        stance.growth += 0.12
    if inflation > 2.0:
        stance.control += 0.05

    stance = _normalize(stance)
    stance.urgency = min(1.0, max(float(risk_scores["social_risk"]), float(risk_scores["fiscal_risk"]), float(risk_scores["shortage_risk"])))
    stance.confidence = max(0.05, min(1.0, 1.0 - float(observations["volatility"]) / 15.0))
    stance.trust_in_operator = max(0.1, min(1.0, stance.trust_in_operator * 0.98 + stance.confidence * 0.02))
    return stance
