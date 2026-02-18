from __future__ import annotations

from copy import deepcopy

from shinon_os.core import intents
from shinon_os.core.blocks.interpret import parse_input
from shinon_os.core.blocks.narrate import render_action_report, render_view_header
from shinon_os.core.blocks.plan import create_plan
from shinon_os.core.blocks.sense import build_observations
from shinon_os.core.blocks.stance import update_stance
from shinon_os.core.formatting import render_table
from shinon_os.core.memory import KernelMemory
from shinon_os.core.types import ChatTurnModel, KernelResponse, StanceState
from shinon_os.i18n import set_lang, t
from shinon_os.sim.engine import SimulationEngine
from shinon_os.sim.model import GameState, WorldState
from shinon_os.util.logging_setup import JsonlRotatingLogger


class ShinonKernel:
    def __init__(self, engine: SimulationEngine, logger: JsonlRotatingLogger) -> None:
        self.engine = engine
        self.logger = logger
        self.stance = StanceState()
        self.memory = KernelMemory(limit=12)
        self.current_view = "dashboard"
        self.last_world_snapshot: WorldState | None = None

    def _render_dashboard(self, state: GameState) -> str:
        world = state.world
        shortages = [good_id for good_id, row in state.market.items() if row.supply < row.demand * 0.88]
        movers = sorted(
            (
                (good_id, ((row.price - row.last_price) / row.last_price * 100.0) if row.last_price > 0 else 0.0)
                for good_id, row in state.market.items()
            ),
            key=lambda item: abs(item[1]),
            reverse=True,
        )[:3]
        active_rows = [
            f"{policy_id} (remaining {runtime.remaining_ticks}, cooldown {runtime.cooldown_ticks})"
            for policy_id, runtime in sorted(state.active_policies.items())
            if runtime.remaining_ticks > 0
        ]
        top_line = ", ".join(f"{good}:{delta:+.2f}%" for good, delta in movers) if movers else t("kernel.none")
        collapse_line = t("cmd.collapse.active") if self.engine.collapse_active() else t("cmd.collapse.inactive")
        return "\n".join(
            [
                t("kernel.view.dashboard"),
                f"turn={world.turn} treasury={world.treasury} population={world.population}",
                f"prosperity={world.prosperity:.2f} stability={world.stability:.2f} unrest={world.unrest:.2f} tech={world.tech_level:.2f}",
                f"shortages: {', '.join(shortages) if shortages else t('kernel.none')}",
                f"top movers: {top_line}",
                f"active policies: {', '.join(active_rows) if active_rows else t('kernel.none')}",
                f"stance mix: control={self.stance.control:.2f} growth={self.stance.growth:.2f} survival={self.stance.survival:.2f}",
                collapse_line,
            ]
        )

    def _render_market(self, state: GameState) -> str:
        rows = []
        for good_id, item in sorted(state.market.items()):
            delta = ((item.price - item.last_price) / item.last_price * 100.0) if item.last_price > 0 else 0.0
            rows.append(
                [
                    good_id,
                    f"{item.supply:.2f}",
                    f"{item.demand:.2f}",
                    f"{item.price:.2f}",
                    f"{delta:+.2f}%",
                ]
            )
        table = render_table(["good", "supply", "demand", "price", "delta"], rows)
        return f"{t('kernel.view.market')}\n{table}"

    def _render_policies(self, state: GameState) -> str:
        rows = []
        for row in self.engine.policy_status(state):
            rows.append(
                [
                    str(row["id"]),
                    str(row["status"]),
                    str(row["remaining_ticks"]),
                    str(row["cooldown_ticks"]),
                    str(row["label"]),
                ]
            )
        table = render_table(["policy", "status", "rem", "cd", "label"], rows)
        return f"{t('kernel.view.policies')}\n{table}\n\n{t('kernel.enact.syntax')}"

    def _render_industry(self, state: GameState) -> str:
        rows = []
        for sector_id, sector in sorted(state.sectors.items()):
            rows.append(
                [
                    sector_id,
                    f"{sector.capacity:.2f}",
                    f"{sector.efficiency:.2f}",
                    f"{sector.upkeep:.2f}",
                ]
            )
        table = render_table(["sector", "capacity", "efficiency", "upkeep"], rows)
        return f"{t('kernel.view.industry')}\n{table}"

    def _render_history(self) -> str:
        history_rows = self.engine.repo.history(limit=10)
        if not history_rows:
            return f"{t('kernel.view.history')}\n{t('kernel.history.empty')}"
        rows = []
        for row in history_rows:
            summary = row["summary"]
            rows.append(
                [
                    str(row["turn"]),
                    str(row["action"]),
                    str(row["cost"]),
                    f"{float(summary.get('inflation', 0.0)):+.2f}%",
                    ",".join(summary.get("events", [])) or t("kernel.none"),
                ]
            )
        table = render_table(["turn", "action", "cost", "inflation", "events"], rows)
        return f"{t('kernel.view.history')}\n{table}"

    def _render_explain(self, topic: str) -> str:
        normalized = topic.strip().lower()
        if normalized in {"price", "prices"}:
            return f"{t('kernel.view.explain')}\n{t('kernel.explain.prices')}\n{t('kernel.explain.shortages')}"
        if normalized in {"shortage", "shortages"}:
            return f"{t('kernel.view.explain')}\n{t('kernel.explain.shortages2')}"
        if normalized.startswith("policy "):
            policy_id = normalized.split(" ", 1)[1].upper()
            definition = self.engine.bundle.policies.get(policy_id)
            if definition is None:
                return f"{t('kernel.view.explain')}\n{t('kernel.explain.unknown_policy')}"
            return f"{t('kernel.view.explain')}\n{policy_id}: {self.engine._policy_desc(policy_id)}"
        return f"{t('kernel.view.explain')}\n{t('kernel.explain.topics')}\n{t('kernel.explain.hint')}"

    def _render_unlock_list(self, state: GameState) -> str:
        rows_data = self.engine.unlock_status(state)
        if not rows_data:
            return f"{t('cmd.unlock.header')}\n{t('cmd.unlock.none')}"
        rows: list[list[str]] = []
        for row in rows_data:
            status = "unlocked" if bool(row["unlocked"]) else "locked"
            rows.append(
                [
                    str(row["policy_id"]),
                    status,
                    str(row["unlocked_turn"]),
                    str(row["source"]),
                ]
            )
        table = render_table(["policy", "status", "turn", "source"], rows)
        next_unlock = self.engine.repo.get_int_meta("next_unlock_turn", 0)
        return f"{t('cmd.unlock.header')}\n{table}\n{t('cmd.unlock.next')}: {next_unlock}"

    def _render_goals(self, state: GameState) -> str:
        rows_data = self.engine.soft_goals(state)
        rows: list[list[str]] = []
        for row in rows_data:
            rows.append(
                [
                    str(row["id"]),
                    str(row["title"]),
                    f"{float(row['current']):.2f}",
                    f"{row['operator']} {float(row['target']):.2f}",
                    "yes" if bool(row["done"]) else "no",
                ]
            )
        table = render_table(["id", "goal", "current", "target", "done"], rows)
        return f"{t('cmd.goals.header')}\n{table}"

    def _render_intel(self, state: GameState) -> str:
        hint = self.engine.intel_hint(state, auto=False)
        if hint is None:
            return f"{t('cmd.intel.header')}\n{t('cmd.intel.none')}"
        return f"{t('cmd.intel.header')}\n- {hint['text']}"

    def _render_view(self, intent_kind: str, state: GameState, topic: str = "general") -> tuple[str, str]:
        if intent_kind == intents.VIEW_DASH:
            self.current_view = "dashboard"
            return self.current_view, self._render_dashboard(state)
        if intent_kind == intents.VIEW_MARKET:
            self.current_view = "market"
            return self.current_view, self._render_market(state)
        if intent_kind == intents.VIEW_POLICIES:
            self.current_view = "policies"
            return self.current_view, self._render_policies(state)
        if intent_kind == intents.VIEW_INDUSTRY:
            self.current_view = "industry"
            return self.current_view, self._render_industry(state)
        if intent_kind == intents.VIEW_HISTORY:
            self.current_view = "history"
            return self.current_view, self._render_history()
        if intent_kind == intents.EXPLAIN:
            self.current_view = "explain"
            return self.current_view, self._render_explain(topic)
        self.current_view = "dashboard"
        return self.current_view, self._render_dashboard(state)

    def _policy_target_types(self) -> dict[str, str]:
        return {policy_id: definition.target_type for policy_id, definition in self.engine.bundle.policies.items()}

    def _chat_prompt_for_missing(self, missing_params: list[str], policy_id: str) -> str:
        if "target" in missing_params:
            return t("kernel.missing_target", policy_id=policy_id)
        return t("kernel.missing_context", policy_id=policy_id)

    def _chat_response(
        self,
        intent_kind: str,
        content: str,
        turn_advanced: bool,
        raw_message: str,
        executed_action: str | None = None,
        events: list[str] | None = None,
        locale_changed: bool = False,
    ) -> KernelResponse:
        events = events or []
        return KernelResponse(
            output=content,
            current_view=self.current_view,
            turn_advanced=turn_advanced,
            locale_changed=locale_changed,
            chat_turn=ChatTurnModel(
                user_message=raw_message,
                recognized_intent=intent_kind,
                executed_action=executed_action,
                turn_advanced=turn_advanced,
                delta_summary=content.splitlines()[2] if len(content.splitlines()) > 2 else "",
                events=events,
                follow_up_prompt=t("kernel.followup"),
            ),
        )

    def handle(self, raw_command: str) -> KernelResponse:
        state = self.engine.load_state()
        observations = build_observations(state, self.last_world_snapshot)
        intent = parse_input(raw_command, self.current_view, policy_target_types=self._policy_target_types())

        if intent.kind == intents.QUIT:
            return KernelResponse(
                output=t("kernel.shutdown_ack"),
                current_view=self.current_view,
                turn_advanced=False,
                should_quit=True,
                chat_turn=ChatTurnModel(
                    user_message=raw_command,
                    recognized_intent=intents.QUIT,
                    executed_action=None,
                    turn_advanced=False,
                    delta_summary="",
                    events=[],
                    follow_up_prompt="",
                ),
            )

        if intent.kind == intents.LANG:
            code = str(intent.args.get("code", "")).lower()
            if code not in {"de", "en"}:
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"{t('kernel.online')}\n{t('cmd.lang.invalid', code=code)}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )
            self.engine.repo.set_language(code)
            set_lang(code)
            return self._chat_response(
                intent_kind=intent.kind,
                content=f"{t('kernel.online')}\n{t('cmd.lang.changed', code=code)}",
                turn_advanced=False,
                raw_message=raw_command,
                locale_changed=True,
            )

        if intent.kind == intents.UNLOCK_LIST:
            content = self._render_unlock_list(state)
            return self._chat_response(intent_kind=intent.kind, content=content, turn_advanced=False, raw_message=raw_command)

        if intent.kind == intents.SHOW_GOALS:
            content = self._render_goals(state)
            return self._chat_response(intent_kind=intent.kind, content=content, turn_advanced=False, raw_message=raw_command)

        if intent.kind == intents.INTEL:
            content = self._render_intel(state)
            return self._chat_response(intent_kind=intent.kind, content=content, turn_advanced=False, raw_message=raw_command)

        if intent.kind == intents.ENACT_POLICY:
            if "invalid" in intent.args:
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"{t('kernel.online')}\nINVALID PARAM {intent.args['invalid']}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )
            if intent.missing_params:
                policy_id = str(intent.args.get("policy_id", "UNKNOWN"))
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"{t('kernel.online')}\n{self._chat_prompt_for_missing(intent.missing_params, policy_id)}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )
            if not intent.auto_execute:
                policy_id = str(intent.args.get("policy_id", "UNKNOWN"))
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"{t('kernel.online')}\n{t('kernel.intent_ambiguous', policy_id=policy_id)}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )

            result = self.engine.advance_turn(
                policy_id=str(intent.args["policy_id"]),
                magnitude=intent.args.get("magnitude"),
                target=intent.args.get("target"),
            )
            if not result.ok:
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"{t('kernel.online')}\n{result.message}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )

            new_state = self.engine.load_state()
            new_observations = build_observations(new_state, self.last_world_snapshot)
            self.stance = update_stance(new_observations, self.stance)
            plan = create_plan(intent, self.stance, new_observations, self.engine.policy_status(new_state))
            seed = self.engine.repo.get_seed() or 0
            output = render_action_report(seed, result, plan, self.stance)

            auto_hint = self.engine.intel_hint(new_state, auto=True)
            if auto_hint:
                output = output + f"\n{t('kernel.auto_intel.prefix')}: {auto_hint['text']}"

            self.memory.record(
                {
                    "turn": new_state.world.turn,
                    "action": result.action_label,
                    "shortages": result.shortages,
                    "events": [event["id"] for event in result.events],
                    "treasury": new_state.world.treasury,
                }
            )
            self.current_view = "dashboard"
            self.last_world_snapshot = deepcopy(new_state.world)
            return self._chat_response(
                intent_kind=intent.kind,
                content=output,
                turn_advanced=True,
                raw_message=raw_command,
                executed_action=result.action_label,
                events=[event["id"] for event in result.events],
            )

        topic = str(intent.args.get("topic", "general"))
        self.stance = update_stance(observations, self.stance)
        plan = create_plan(intent, self.stance, observations, self.engine.policy_status(state))
        view_name, body = self._render_view(intent.kind, state, topic=topic)
        output = (
            render_view_header(state.world, self.stance, plan)
            + "\n\n"
            + body
            + f"\n\n{t('kernel.advisor.label')}: "
            + (", ".join(plan.recommendations) if plan.recommendations else t("kernel.none"))
            + f"\n{t('kernel.next.label')}: "
            + ", ".join(plan.options)
        )
        self.last_world_snapshot = deepcopy(state.world)
        self.logger.debug({"where": "kernel.view", "view": view_name, "turn": state.world.turn})
        return self._chat_response(
            intent_kind=intent.kind,
            content=output,
            turn_advanced=False,
            raw_message=raw_command,
        )
