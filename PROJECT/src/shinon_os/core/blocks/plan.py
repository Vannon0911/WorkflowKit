from __future__ import annotations

from shinon_os.core import intents
from shinon_os.core.types import Intent, Plan, StanceState
from shinon_os.i18n import t


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
        "PRICE_STABILIZER": (0.9 * inflation + 0.5 * shortages, 0.5, 0.7),
        "LOGISTICS_PUSH": (1.1 * shortages, 1.2, 0.5),
        "INDUSTRIAL_MODERNIZATION": (0.6 * shortages, 1.3, 0.4),
        "STRATEGIC_RESERVE": (1.4 * shortages, 0.6, 0.8),
        "SOCIAL_COMPACT": (1.0 * unrest_risk, 0.4, 0.9),
        "SOS_CREDIT": (2.2 * fiscal_risk, 0.2, 2.0),
        "RATIONING_PLUS": (2.0 * shortages + unrest_risk, 0.1, 1.8),
    }
    control_gain, growth_gain, survival_gain = heuristics.get(policy_id, (0.3, 0.3, 0.3))
    return (
        stance.control * control_gain
        + stance.growth * growth_gain
        + stance.survival * survival_gain
    )


def _predictive_note(policy_id: str) -> str:
    notes = {
        "TAX_ADJUST": t("plan.note.tax_adjust"),
        "SUBSIDY_SECTOR": t("plan.note.subsidy_sector"),
        "FUND_RESEARCH": t("plan.note.fund_research"),
        "BUILD_INFRA": t("plan.note.build_infra"),
        "SECURITY_BUDGET": t("plan.note.security_budget"),
        "RATIONING": t("plan.note.rationing"),
        "WORK_HOURS_REFORM": t("plan.note.work_hours_reform"),
        "IMPORT_PROGRAM": t("plan.note.import_program"),
        "PRICE_STABILIZER": t("plan.note.price_stabilizer"),
        "LOGISTICS_PUSH": t("plan.note.logistics_push"),
        "INDUSTRIAL_MODERNIZATION": t("plan.note.industrial_modernization"),
        "STRATEGIC_RESERVE": t("plan.note.strategic_reserve"),
        "SOCIAL_COMPACT": t("plan.note.social_compact"),
        "SOS_CREDIT": t("plan.note.sos_credit"),
        "RATIONING_PLUS": t("plan.note.rationing_plus"),
    }
    return notes.get(policy_id, t("plan.note.uncertain"))


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
            status_line=t("plan.status.armed", policy_id=selected),
            recommendations=recommendations,
            predicted_impact=_predictive_note(selected),
            options=["dashboard", "market", "policies", "history", "explain prices", "unlock list", "show goals", "intel"],
        )

    return Plan(
        acts=["INFORM", "RECOMMEND"],
        status_line=t("plan.status.monitoring"),
        recommendations=recommendations,
        predicted_impact=t("plan.status.no_advance"),
        options=[
            "dashboard",
            "market",
            "policies",
            "industry",
            "history",
            "explain prices",
            "unlock list",
            "show goals",
            "intel",
            "enact <POLICY_ID> [magnitude] [target]",
        ],
    )
