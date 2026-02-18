from __future__ import annotations

import math
from dataclasses import dataclass

from shinon_os.sim.model import GameState
from shinon_os.sim.worldgen import DataBundle, PolicyDefinition


@dataclass(frozen=True)
class ActionRequest:
    policy_id: str
    magnitude: float
    target: str | None
    immediate_cost: int


def _step_aligned(value: float, min_value: float, step: float) -> bool:
    if step <= 0:
        return True
    ticks = round((value - min_value) / step)
    reconstructed = min_value + ticks * step
    return math.isclose(value, reconstructed, rel_tol=1e-9, abs_tol=1e-9)


def normalize_magnitude(policy: PolicyDefinition, raw_magnitude: float | None) -> tuple[float | None, str | None]:
    if raw_magnitude is None:
        raw_magnitude = policy.magnitude["default"]
    min_value = policy.magnitude["min"]
    max_value = policy.magnitude["max"]
    step = policy.magnitude["step"]

    magnitude = float(raw_magnitude)
    if magnitude < min_value or magnitude > max_value:
        return None, f"INVALID PARAM magnitude out of range [{min_value}, {max_value}]"
    if not _step_aligned(magnitude, min_value, step):
        return None, f"INVALID PARAM magnitude must follow step {step}"
    return magnitude, None


def validate_target(policy: PolicyDefinition, target: str | None, bundle: DataBundle) -> str | None:
    if policy.target_type == "none":
        return None
    if target is None:
        return "INVALID PARAM missing target"
    if policy.target_type == "sector":
        if target not in bundle.sector_ids():
            return "INVALID PARAM unknown sector target"
        return None
    if policy.target_type == "good":
        if target not in bundle.goods_by_id():
            return "INVALID PARAM unknown good target"
        return None
    return None


def validate_action(
    state: GameState,
    bundle: DataBundle,
    policy: PolicyDefinition,
    raw_magnitude: float | None,
    target: str | None,
) -> tuple[ActionRequest | None, str | None]:
    runtime = state.active_policies.get(policy.policy_id)
    if runtime and (runtime.remaining_ticks > 0 or runtime.cooldown_ticks > 0):
        return None, "INVALID PARAM policy currently active or cooling down"

    target_error = validate_target(policy, target, bundle)
    if target_error:
        return None, target_error

    magnitude, magnitude_error = normalize_magnitude(policy, raw_magnitude)
    if magnitude_error:
        return None, magnitude_error
    assert magnitude is not None

    min_treasury = int(policy.constraints.get("min_treasury", 0))
    immediate_cost = int(round(policy.cost * max(abs(magnitude), 0.25)))
    if state.world.treasury < min_treasury or state.world.treasury < immediate_cost:
        return None, "INVALID PARAM insufficient treasury"

    return (
        ActionRequest(
            policy_id=policy.policy_id,
            magnitude=magnitude,
            target=target,
            immediate_cost=immediate_cost,
        ),
        None,
    )
