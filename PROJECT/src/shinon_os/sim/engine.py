from __future__ import annotations

from copy import deepcopy
from typing import Any

from shinon_os.i18n import t
from shinon_os.persistence.repo import START_LOADOUT, StateRepository
from shinon_os.sim.actions import validate_action
from shinon_os.sim.economy import clamp, simulate_market
from shinon_os.sim.events import apply_event, choose_event
from shinon_os.sim.metrics import compute_derived_metrics
from shinon_os.sim.model import GameState, PolicyRuntime, SimResult, WorldState
from shinon_os.sim.worldgen import DataBundle, build_initial_state
from shinon_os.util.logging_setup import JsonlRotatingLogger
from shinon_os.util.timeutil import utc_now_iso

EMERGENCY_POLICY_IDS = {"SOS_CREDIT", "RATIONING_PLUS"}


class SimulationEngine:
    def __init__(self, bundle: DataBundle, repo: StateRepository, logger: JsonlRotatingLogger) -> None:
        self.bundle = bundle
        self.repo = repo
        self.logger = logger

    def ensure_game(self, seed: int = 42) -> None:
        if not self.repo.has_game():
            self.new_game(seed)

    def new_game(self, seed: int) -> None:
        state = build_initial_state(self.bundle)
        state.unlocked_policies = set(START_LOADOUT)
        self.repo.init_new_game(seed=seed, state=state)

    def load_state(self) -> GameState:
        return self.repo.load_state(self.bundle.sector_io_defs())

    def collapse_active(self) -> bool:
        return self.repo.get_bool_meta("collapse_active", False)

    def _policy_label(self, policy_id: str) -> str:
        definition = self.bundle.policies[policy_id]
        if definition.label_key:
            return t(definition.label_key)
        return definition.label

    def _policy_desc(self, policy_id: str) -> str:
        definition = self.bundle.policies[policy_id]
        if definition.description_key:
            return t(definition.description_key)
        return definition.description

    def _policy_unlocked(self, state: GameState, policy_id: str) -> bool:
        if policy_id in EMERGENCY_POLICY_IDS:
            return self.collapse_active()
        return policy_id in state.unlocked_policies

    def policy_status(self, state: GameState) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for policy_id, definition in self.bundle.policies.items():
            runtime = state.active_policies.get(policy_id)
            unlocked = self._policy_unlocked(state, policy_id)
            status = "locked" if not unlocked else "available"
            remaining = 0
            cooldown = 0
            if unlocked and runtime:
                if runtime.remaining_ticks > 0:
                    status = "active"
                    remaining = runtime.remaining_ticks
                elif runtime.cooldown_ticks > 0:
                    status = "cooldown"
                    cooldown = runtime.cooldown_ticks
            rows.append(
                {
                    "id": policy_id,
                    "label": t(definition.label_key) if definition.label_key else definition.label,
                    "status": status,
                    "remaining_ticks": remaining,
                    "cooldown_ticks": cooldown,
                    "description": t(definition.description_key) if definition.description_key else definition.description,
                    "is_emergency": policy_id in EMERGENCY_POLICY_IDS,
                }
            )
        rows.sort(key=lambda row: row["id"])
        return rows

    def unlock_status(self, state: GameState) -> list[dict[str, Any]]:
        rows = self.repo.unlocked_policy_rows()
        index = {str(row["policy_id"]): row for row in rows}
        result: list[dict[str, Any]] = []
        for policy_id in sorted(self.bundle.policies):
            row = index.get(policy_id)
            unlocked = self._policy_unlocked(state, policy_id)
            result.append(
                {
                    "policy_id": policy_id,
                    "label": self._policy_label(policy_id),
                    "unlocked": unlocked,
                    "unlocked_turn": int(row["unlocked_turn"]) if row else -1,
                    "source": str(row["source"]) if row else ("collapse_only" if policy_id in EMERGENCY_POLICY_IDS else "locked"),
                }
            )
        return result

    def soft_goals(self, state: GameState) -> list[dict[str, Any]]:
        values = {
            "treasury": float(state.world.treasury),
            "population": float(state.world.population),
            "prosperity": float(state.world.prosperity),
            "stability": float(state.world.stability),
            "unrest": float(state.world.unrest),
            "tech_level": float(state.world.tech_level),
        }
        rows: list[dict[str, Any]] = []
        for goal in self.bundle.soft_goals:
            current = values.get(goal.metric, 0.0)
            if goal.operator == ">=":
                done = current >= goal.target
                ratio = 1.0 if goal.target == 0 else min(1.0, current / goal.target)
            else:
                done = current <= goal.target
                ratio = 1.0 if current <= 0 else min(1.0, goal.target / current)
            rows.append(
                {
                    "id": goal.goal_id,
                    "title": t(goal.title_key),
                    "description": t(goal.description_key),
                    "metric": goal.metric,
                    "operator": goal.operator,
                    "target": goal.target,
                    "current": current,
                    "done": done,
                    "progress": max(0.0, min(1.0, ratio)),
                }
            )
        return rows

    def _hint_matches(self, state: GameState, conditions: dict[str, Any]) -> bool:
        shortages = sum(1 for row in state.market.values() if row.supply < row.demand * 0.88)
        if shortages < int(conditions.get("min_shortages", 0)):
            return False
        if state.world.treasury > int(conditions.get("max_treasury", 10**9)):
            return False
        if state.world.unrest < float(conditions.get("min_unrest", 0.0)):
            return False
        if state.world.stability < float(conditions.get("min_stability", 0.0)):
            return False
        if state.world.unrest > float(conditions.get("max_unrest", 100.0)):
            return False
        return True

    def _pick_hint_id(self, state: GameState, avoid_hint_id: str) -> str | None:
        candidates: list[str] = []
        for hint in self.bundle.intel_hints:
            if not self._hint_matches(state, hint.conditions):
                continue
            candidates.append(hint.hint_id)
        if not candidates:
            return None
        for hint_id in candidates:
            if hint_id != avoid_hint_id:
                return hint_id
        return candidates[0]

    def intel_hint(self, state: GameState, auto: bool = False) -> dict[str, str] | None:
        last_hint_id = self.repo.get_str_meta("last_intel_hint_id", "")
        if auto:
            last_turn = self.repo.get_int_meta("last_auto_intel_turn", -9999)
            if state.world.turn - last_turn < 5:
                return None
        hint_id = self._pick_hint_id(state, last_hint_id)
        if hint_id is None:
            return None
        hint_def = next((row for row in self.bundle.intel_hints if row.hint_id == hint_id), None)
        if hint_def is None:
            return None
        if auto:
            self.repo.set_int_meta("last_auto_intel_turn", state.world.turn)
        self.repo.set_str_meta("last_intel_hint_id", hint_id)
        return {"id": hint_id, "text": t(hint_def.text_key)}

    def _collect_policy_effects(self, state: GameState) -> dict[str, Any]:
        effects: dict[str, Any] = {
            "world_add": {},
            "treasury_income": 0.0,
            "treasury_upkeep": 0.0,
            "global_output_mult": 0.0,
            "sector_output_mult": {},
            "sector_efficiency_add": {},
            "good_supply_add": {},
            "good_demand_mult": {},
            "good_price_mult": {},
            "import_cost": 0.0,
            "shortage_unrest_factor_add": 0.0,
        }

        def add_map(target: dict[str, float], key: str, value: float) -> None:
            target[key] = float(target.get(key, 0.0) + value)

        for runtime in state.active_policies.values():
            if runtime.remaining_ticks <= 0:
                continue
            definition = self.bundle.policies[runtime.policy_id]
            magnitude = runtime.magnitude
            target = runtime.state.get("target")
            definition_effects = definition.effects

            for key, value in definition_effects.get("world_add", {}).items():
                add_map(effects["world_add"], key, float(value) * magnitude)

            effects["treasury_income"] += float(definition_effects.get("treasury_income_per_turn", 0.0)) * magnitude
            effects["treasury_upkeep"] += abs(magnitude) * float(definition_effects.get("treasury_upkeep_per_turn", 0.0))
            effects["global_output_mult"] += float(definition_effects.get("global_output_mult", 0.0)) * magnitude
            effects["shortage_unrest_factor_add"] += float(definition_effects.get("shortage_unrest_factor_add", 0.0)) * magnitude

            for key, value in definition_effects.get("sector_output_mult", {}).items():
                resolved = target if key == "target" else key
                if resolved:
                    add_map(effects["sector_output_mult"], resolved, float(value) * magnitude)
            for key, value in definition_effects.get("sector_efficiency_add", {}).items():
                resolved = target if key == "target" else key
                if resolved:
                    add_map(effects["sector_efficiency_add"], resolved, float(value) * magnitude)
            for key, value in definition_effects.get("good_supply_add", {}).items():
                resolved = target if key == "target" else key
                if resolved:
                    amount = float(value) * magnitude
                    add_map(effects["good_supply_add"], resolved, amount)
                    unit_cost = float(definition_effects.get("import_cost_per_unit", 0.0))
                    if unit_cost > 0:
                        effects["import_cost"] += max(0.0, amount) * unit_cost
            for key, value in definition_effects.get("good_demand_mult", {}).items():
                resolved = target if key == "target" else key
                if resolved:
                    add_map(effects["good_demand_mult"], resolved, float(value) * magnitude)

            delay = int(runtime.state.get("delay_left", 0))
            if "sector_capacity_add" in definition_effects:
                if delay > 0:
                    runtime.state["delay_left"] = delay - 1
                elif not bool(runtime.state.get("capacity_applied", False)):
                    for key, value in definition_effects.get("sector_capacity_add", {}).items():
                        resolved = target if key == "target" else key
                        if resolved and resolved in state.sectors:
                            state.sectors[resolved].capacity += float(value) * magnitude
                    runtime.state["capacity_applied"] = True

        return effects

    def _tick_policy_runtimes(self, state: GameState) -> None:
        remove_ids: list[str] = []
        for policy_id, runtime in state.active_policies.items():
            definition = self.bundle.policies[policy_id]
            if runtime.remaining_ticks > 0:
                runtime.remaining_ticks -= 1
                if runtime.remaining_ticks == 0:
                    runtime.cooldown_ticks = definition.cooldown_ticks
            elif runtime.cooldown_ticks > 0:
                runtime.cooldown_ticks -= 1

            if runtime.remaining_ticks <= 0 and runtime.cooldown_ticks <= 0:
                remove_ids.append(policy_id)

        for policy_id in remove_ids:
            del state.active_policies[policy_id]

    def _invalid_result(self, world: WorldState, message: str) -> SimResult:
        snapshot = deepcopy(world)
        return SimResult(
            ok=False,
            message=message,
            turn_advanced=False,
            action_label="none",
            world_before=snapshot,
            world_after=snapshot,
            top_price_movers=[],
            shortages=[],
            inflation=0.0,
            volatility=0.0,
            events=[],
            errors=[message],
        )

    def _maybe_unlock_policy(self, state: GameState) -> list[str]:
        if state.world.turn <= 0:
            return []
        available_rules = sorted(self.bundle.unlocks, key=lambda row: (row.min_turn, row.min_actions, row.policy_id))
        candidates = [
            row
            for row in available_rules
            if row.policy_id not in state.unlocked_policies
            and row.policy_id not in EMERGENCY_POLICY_IDS
            and state.world.turn >= row.min_turn
            and state.world.turn >= row.min_actions
        ]
        if not candidates:
            return []

        next_unlock_turn = self.repo.get_int_meta("next_unlock_turn", 0)
        if state.world.turn >= 6 and state.world.turn < next_unlock_turn:
            return []

        selected = candidates[0]
        state.unlocked_policies.add(selected.policy_id)
        self.repo.unlock_policy(selected.policy_id, turn=state.world.turn, source=selected.source)

        if state.world.turn >= 6:
            self.repo.set_int_meta("next_unlock_turn", state.world.turn + 3)
        return [selected.policy_id]

    def _update_collapse_state(self, world: WorldState, trailing_3_cashflow: float) -> bool:
        collapse_active = self.repo.get_bool_meta("collapse_active", False)
        recovery_streak = self.repo.get_int_meta("collapse_recovery_streak", 0)

        if world.treasury < 0 and trailing_3_cashflow < 0:
            collapse_active = True
            recovery_streak = 0
        elif collapse_active and world.treasury >= 0 and trailing_3_cashflow >= 0:
            recovery_streak += 1
            if recovery_streak >= 2:
                collapse_active = False
                recovery_streak = 0
        elif collapse_active:
            recovery_streak = 0
        else:
            recovery_streak = 0

        self.repo.set_bool_meta("collapse_active", collapse_active)
        self.repo.set_int_meta("collapse_recovery_streak", recovery_streak)
        return collapse_active

    def advance_turn(self, policy_id: str, magnitude: float | None, target: str | None) -> SimResult:
        try:
            state = self.load_state()
            seed = self.repo.get_seed()
            if seed is None:
                return self._invalid_result(state.world, "INVALID PARAM missing seed in DB")

            policy = self.bundle.policies.get(policy_id)
            if policy is None:
                return self._invalid_result(state.world, "INVALID PARAM unknown policy")
            if not self._policy_unlocked(state, policy_id):
                return self._invalid_result(state.world, "INVALID PARAM policy is locked")

            action, error = validate_action(state=state, bundle=self.bundle, policy=policy, raw_magnitude=magnitude, target=target)
            if error:
                return self._invalid_result(state.world, error)
            assert action is not None

            world_before = deepcopy(state.world)
            market_before = deepcopy(state.market)

            state.world.treasury -= action.immediate_cost
            state.active_policies[action.policy_id] = PolicyRuntime(
                policy_id=action.policy_id,
                remaining_ticks=policy.duration_ticks,
                cooldown_ticks=0,
                magnitude=action.magnitude,
                state={
                    "target": action.target,
                    "delay_left": int(policy.effects.get("capacity_delay", 0)),
                    "capacity_applied": False,
                },
            )

            state.world.turn += 1
            state.world.last_action_ts = utc_now_iso()
            effects = self._collect_policy_effects(state)

            upkeep = sum(sector.upkeep for sector in state.sectors.values())
            state.world.treasury -= int(round(upkeep))

            base_income = int(round(state.world.population * (0.012 + state.world.prosperity / 9000.0)))
            state.world.treasury += base_income + int(round(effects["treasury_income"]))
            state.world.treasury -= int(round(effects["treasury_upkeep"] + effects["import_cost"]))

            state.market = simulate_market(
                world=state.world,
                market=state.market,
                sectors=state.sectors,
                goods_meta=self.bundle.goods_by_id(),
                economy_cfg=self.bundle.config["economy"],
                population_needs=self.bundle.config["population_needs"],
                effects=effects,
                seed=seed,
                turn=state.world.turn,
            )

            derived = compute_derived_metrics(
                before=market_before,
                after=state.market,
                shortage_threshold=float(self.bundle.config["economy"]["shortage_threshold"]),
            )

            shortage_count = len(derived["shortages"])
            shortage_pressure = shortage_count * (1.5 + float(effects["shortage_unrest_factor_add"]))
            state.world.unrest += shortage_pressure + max(0.0, derived["inflation"]) * 0.15
            state.world.prosperity += -shortage_count * 0.8 - max(0.0, derived["inflation"]) * 0.22 + state.world.tech_level * 0.01
            state.world.stability += -state.world.unrest * 0.02
            state.world.tech_level += 0.2

            for key, value in effects["world_add"].items():
                if key == "treasury":
                    state.world.treasury += int(round(value))
                else:
                    current = float(getattr(state.world, key))
                    setattr(state.world, key, current + float(value))

            event_rows: list[dict[str, Any]] = []
            event = choose_event(
                events=self.bundle.events,
                world=state.world,
                market=state.market,
                seed=seed,
                turn=state.world.turn,
                event_chance=float(self.bundle.config["economy"]["event_chance"]),
            )
            if event is not None:
                event_rows.append(apply_event(event, state.world, state.market, state.sectors))

            for good_id, item in state.market.items():
                meta = self.bundle.goods_by_id()[good_id]
                item.price = clamp(item.price, float(meta["min_price"]), float(meta["max_price"]))

            derived = compute_derived_metrics(
                before=market_before,
                after=state.market,
                shortage_threshold=float(self.bundle.config["economy"]["shortage_threshold"]),
            )

            pop_delta = int((state.world.prosperity - state.world.unrest - 30.0) / 200.0)
            state.world.population = max(10000, state.world.population + pop_delta)
            state.world.treasury = int(round(state.world.treasury))
            state.world.prosperity = clamp(state.world.prosperity, 0.0, 100.0)
            state.world.stability = clamp(state.world.stability, 0.0, 100.0)
            state.world.unrest = clamp(state.world.unrest, 0.0, 100.0)
            state.world.tech_level = clamp(state.world.tech_level, 0.0, 100.0)

            net_cashflow = float(state.world.treasury - world_before.treasury)
            trailing_3_cashflow = self.repo.trailing_cashflow(window=3, include_current=net_cashflow)
            collapse_active = self._update_collapse_state(state.world, trailing_3_cashflow)

            unlocked_now = self._maybe_unlock_policy(state)

            self._tick_policy_runtimes(state)
            self.repo.save_state(state)

            total_cost = action.immediate_cost + int(round(upkeep + effects["treasury_upkeep"] + effects["import_cost"]))
            summary = {
                "shortages": list(derived["shortages"]),
                "inflation": round(float(derived["inflation"]), 3),
                "volatility": round(float(derived["volatility"]), 3),
                "top_price_movers": [(gid, round(delta, 3)) for gid, delta in derived["top_movers"]],
                "events": [e["id"] for e in event_rows],
                "treasury": state.world.treasury,
                "net_cashflow": round(net_cashflow, 3),
                "trailing_3_cashflow": round(trailing_3_cashflow, 3),
                "collapse_active": collapse_active,
                "unlocked": unlocked_now,
            }
            self.repo.append_history(state.world.turn, action.policy_id, total_cost, summary)
            self.repo.append_events(state.world.turn, event_rows)

            self.logger.sim(
                {
                    "turn": state.world.turn,
                    "action": action.policy_id,
                    "magnitude": action.magnitude,
                    "target": action.target,
                    "shortages": derived["shortages"],
                    "inflation": derived["inflation"],
                    "volatility": derived["volatility"],
                    "events": event_rows,
                    "collapse_active": collapse_active,
                    "unlocked_now": unlocked_now,
                }
            )
            self.logger.debug(
                {
                    "turn": state.world.turn,
                    "policy_effects": effects,
                    "treasury": state.world.treasury,
                }
            )

            return SimResult(
                ok=True,
                message=f"ACTION OK {action.policy_id}",
                turn_advanced=True,
                action_label=action.policy_id,
                world_before=world_before,
                world_after=deepcopy(state.world),
                top_price_movers=[(gid, float(delta)) for gid, delta in derived["top_movers"]],
                shortages=list(derived["shortages"]),
                inflation=float(derived["inflation"]),
                volatility=float(derived["volatility"]),
                events=event_rows,
                errors=[],
            )
        except Exception as exc:  # pragma: no cover - defensive hardening
            self.logger.error({"where": "SimulationEngine.advance_turn", "error": repr(exc)})
            state = self.load_state()
            return self._invalid_result(state.world, f"INVALID PARAM internal error: {exc}")

    def snapshot(self) -> dict[str, Any]:
        state = self.load_state()
        return {
            "turn": state.world.turn,
            "world": {
                "treasury": state.world.treasury,
                "population": state.world.population,
                "prosperity": round(state.world.prosperity, 6),
                "stability": round(state.world.stability, 6),
                "unrest": round(state.world.unrest, 6),
                "tech_level": round(state.world.tech_level, 6),
            },
            "prices": {good_id: round(item.price, 6) for good_id, item in sorted(state.market.items())},
            "unlocked_count": len(state.unlocked_policies),
            "collapse_active": self.collapse_active(),
        }
