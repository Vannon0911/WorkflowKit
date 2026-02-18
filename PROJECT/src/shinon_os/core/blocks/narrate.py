from __future__ import annotations

from shinon_os.core.phrasebank import pick_phrase
from shinon_os.core.types import Plan, StanceState
from shinon_os.sim.model import SimResult, WorldState


def dominant_stance(stance: StanceState) -> str:
    score_map = {
        "CONTROL": stance.control,
        "GROWTH": stance.growth,
        "SURVIVAL": stance.survival,
    }
    return max(score_map, key=score_map.get)


def render_action_report(seed: int, result: SimResult, plan: Plan, stance: StanceState) -> str:
    stance_mode = dominant_stance(stance)
    phrase = pick_phrase(seed, result.world_after.turn, stance_mode)
    movers = ", ".join(f"{good}:{delta:+.2f}%" for good, delta in result.top_price_movers) or "none"
    events_line = ", ".join(event["id"] for event in result.events) if result.events else "none"

    lines = [
        "SHINON // kernel online",
        f"status: ACTION turn={result.world_after.turn} stance={stance_mode} urgency={stance.urgency:.2f} confidence={stance.confidence:.2f}",
        (
            f"delta: treasury {result.world_before.treasury} -> {result.world_after.treasury} "
            f"| unrest {result.world_before.unrest:.2f} -> {result.world_after.unrest:.2f} "
            f"| inflation {result.inflation:+.2f}% | volatility {result.volatility:.2f}%"
        ),
        f"delta: shortages={len(result.shortages)} ({', '.join(result.shortages) if result.shortages else 'none'}) | top movers {movers}",
        f"events: {events_line}",
        f"comment: {phrase}",
        f"advisor: {', '.join(plan.recommendations) if plan.recommendations else 'none'}",
    ]
    return "\n".join(lines)


def render_view_header(world: WorldState, stance: StanceState, plan: Plan) -> str:
    mode = dominant_stance(stance)
    return (
        "SHINON // kernel online\n"
        f"status: VIEW turn={world.turn} stance={mode} urgency={stance.urgency:.2f} confidence={stance.confidence:.2f}\n"
        f"kernel: {plan.status_line}"
    )
