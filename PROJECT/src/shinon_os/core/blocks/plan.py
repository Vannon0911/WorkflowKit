from __future__ import annotations

from shinon_os.core import intents
from shinon_os.core.types import Intent, Plan, StanceState


def _policy_utility(policy_id: str, stance: StanceState, observations: dict[str, object]) -> float:
    shortages = len(observations["shortages"])  # type: ignore[arg-type]
    inflation = max(0.0, float(observations["inflation"]))
    unrest_risk = float(observations["risk_scores"]["social_risk"])  # type: ignore[index]
    fiscal_risk = float(observations["risk_scores"]["fiscal_risk"])  # type: ignore[index]

    heuristics = {
        "SECURITY_BUDGET": (2.4 * unrest_risk, -0.3, 1.2),
        "RATIONING": (1.7 * shortages, -0.2, 1.5),
        "TAX_ADJUST": (0.6 * fiscal_risk, -0.5, 1.0),
        "SUBSIDY_SECTOR": (1.2 * shortages, 1.4, 0.8),
        "FUND_RESEARCH": (0.2, 1.8, 0.6),
        "BUILD_INFRA": (0.8 * shortages, 1.3, 0.7),
        "WORK_HOURS_REFORM": (1.0 * unrest_risk, 0.8, 0.5),
        "IMPORT_PROGRAM": (1.8 * shortages + 0.4 * inflation, 0.3, 1.4),
    }
    control_gain, growth_gain, survival_gain = heuristics.get(policy_id, (0.3, 0.3, 0.3))
    return (
        stance.control * control_gain
        + stance.growth * growth_gain
        + stance.survival * survival_gain
    )


def _predictive_note(policy_id: str) -> str:
    notes = {
        "TAX_ADJUST": "Expected effect: treasury up, social pressure up if magnitude positive.",
        "SUBSIDY_SECTOR": "Expected effect: output lift in target sector, recurring fiscal cost.",
        "FUND_RESEARCH": "Expected effect: tech growth and slower long-term inflation pressure.",
        "BUILD_INFRA": "Expected effect: delayed capacity gain after construction phase.",
        "SECURITY_BUDGET": "Expected effect: unrest down quickly, prosperity drag possible.",
        "RATIONING": "Expected effect: shortage unrest dampened, prosperity reduced.",
        "WORK_HOURS_REFORM": "Expected effect: stability up, aggregate output slightly down.",
        "IMPORT_PROGRAM": "Expected effect: targeted supply relief against treasury outflow.",
    }
    return notes.get(policy_id, "Expected effect: uncertain.")


def create_plan(
    intent: Intent,
    stance: StanceState,
    observations: dict[str, object],
    policy_status_rows: list[dict[str, object]],
) -> Plan:
    ranked = []
    for row in policy_status_rows:
        if row["status"] == "available":
            ranked.append((str(row["id"]), _policy_utility(str(row["id"]), stance, observations)))
    ranked.sort(key=lambda item: item[1], reverse=True)
    recommendations = [policy_id for policy_id, _ in ranked[:3]]

    if intent.kind == intents.ENACT_POLICY:
        selected = str(intent.args.get("policy_id", "UNKNOWN"))
        return Plan(
            acts=["CONFIRM", "INFORM"],
            status_line=f"Action pipeline armed for {selected}",
            recommendations=recommendations,
            predicted_impact=_predictive_note(selected),
            options=["dashboard", "market", "policies", "history", "explain prices"],
        )

    return Plan(
        acts=["INFORM", "RECOMMEND"],
        status_line="Kernel monitoring mode; no turn advancement.",
        recommendations=recommendations,
        predicted_impact="No simulation advance on view commands.",
        options=["dashboard", "market", "policies", "industry", "history", "explain prices", "enact <POLICY_ID> [magnitude] [target]"],
    )
