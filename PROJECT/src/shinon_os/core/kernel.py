from __future__ import annotations

from copy import deepcopy

from shinon_os.core import intents
from shinon_os.core.formatting import render_table
from shinon_os.core.blocks.interpret import parse_input
from shinon_os.core.blocks.narrate import render_action_report, render_view_header
from shinon_os.core.blocks.plan import create_plan
from shinon_os.core.blocks.sense import build_observations
from shinon_os.core.blocks.stance import update_stance
from shinon_os.core.memory import KernelMemory
from shinon_os.core.types import ChatTurnModel, KernelResponse, StanceState
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
        top_line = ", ".join(f"{good}:{delta:+.2f}%" for good, delta in movers) if movers else "none"
        return "\n".join(
            [
                "view: DASHBOARD",
                f"turn={world.turn} treasury={world.treasury} population={world.population}",
                f"prosperity={world.prosperity:.2f} stability={world.stability:.2f} unrest={world.unrest:.2f} tech={world.tech_level:.2f}",
                f"shortages: {', '.join(shortages) if shortages else 'none'}",
                f"top movers: {top_line}",
                f"active policies: {', '.join(active_rows) if active_rows else 'none'}",
                f"stance mix: control={self.stance.control:.2f} growth={self.stance.growth:.2f} survival={self.stance.survival:.2f}",
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
        return "view: MARKET\n" + table

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
        return (
            "view: POLICIES\n"
            + table
            + "\n\nenact syntax: enact <POLICY_ID> [magnitude] [target]"
        )

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
        return "view: INDUSTRY\n" + table

    def _render_history(self) -> str:
        history_rows = self.engine.repo.history(limit=10)
        if not history_rows:
            return "view: HISTORY\n(no turns yet)"
        rows = []
        for row in history_rows:
            summary = row["summary"]
            rows.append(
                [
                    str(row["turn"]),
                    str(row["action"]),
                    str(row["cost"]),
                    f"{float(summary.get('inflation', 0.0)):+.2f}%",
                    ",".join(summary.get("events", [])) or "none",
                ]
            )
        table = render_table(["turn", "action", "cost", "inflation", "events"], rows)
        return "view: HISTORY\n" + table

    def _render_explain(self, topic: str) -> str:
        normalized = topic.strip().lower()
        if normalized in {"price", "prices"}:
            return (
                "view: EXPLAIN\n"
                "prices: demand/supply ratio is damped into [0.5, 2.0], then applied via lerp with k_demand.\n"
                "shortages: supply < demand*(1-shortage_threshold) raises unrest pressure and lowers prosperity."
            )
        if normalized in {"shortage", "shortages"}:
            return (
                "view: EXPLAIN\n"
                "shortages increase social risk. SHINON tracks shortage_risk and pushes CONTROL or SURVIVAL stance."
            )
        if normalized.startswith("policy "):
            policy_id = normalized.split(" ", 1)[1].upper()
            definition = self.engine.bundle.policies.get(policy_id)
            if definition is None:
                return "view: EXPLAIN\nunknown policy"
            return f"view: EXPLAIN\n{policy_id}: {definition.description}"
        return (
            "view: EXPLAIN\n"
            "topics: explain prices | explain shortages | explain policy <POLICY_ID>\n"
            "view prompts do not advance turns. actionable prompts may trigger one turn if intent is clear."
        )

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
            return f"Target fehlt fuer {policy_id}. Nenne bitte ein gueltiges Ziel."
        return f"Mehr Kontext benoetigt fuer {policy_id}."

    def _chat_response(self, intent_kind: str, content: str, turn_advanced: bool, raw_message: str, executed_action: str | None = None, events: list[str] | None = None) -> KernelResponse:
        events = events or []
        return KernelResponse(
            output=content,
            current_view=self.current_view,
            turn_advanced=turn_advanced,
            chat_turn=ChatTurnModel(
                user_message=raw_message,
                recognized_intent=intent_kind,
                executed_action=executed_action,
                turn_advanced=turn_advanced,
                delta_summary=content.splitlines()[2] if len(content.splitlines()) > 2 else "",
                events=events,
                follow_up_prompt="Weiter mit status/markt/measure oder einer neuen Direktive.",
            ),
        )

    def handle(self, raw_command: str) -> KernelResponse:
        state = self.engine.load_state()
        observations = build_observations(state, self.last_world_snapshot)
        intent = parse_input(raw_command, self.current_view, policy_target_types=self._policy_target_types())

        if intent.kind == intents.QUIT:
            return KernelResponse(
                output="SHINON // kernel shutdown sequence acknowledged.",
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

        if intent.kind == intents.ENACT_POLICY:
            if "invalid" in intent.args:
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"SHINON // kernel online\nINVALID PARAM {intent.args['invalid']}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )
            if intent.missing_params:
                policy_id = str(intent.args.get("policy_id", "UNKNOWN"))
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"SHINON // kernel online\n{self._chat_prompt_for_missing(intent.missing_params, policy_id)}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )
            if not intent.auto_execute:
                policy_id = str(intent.args.get("policy_id", "UNKNOWN"))
                return self._chat_response(
                    intent_kind=intent.kind,
                    content=f"SHINON // kernel online\nIntent erkannt ({policy_id}) aber nicht eindeutig genug. Bitte Praezisierung senden.",
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
                    content=f"SHINON // kernel online\n{result.message}",
                    turn_advanced=False,
                    raw_message=raw_command,
                )

            new_state = self.engine.load_state()
            new_observations = build_observations(new_state, self.last_world_snapshot)
            self.stance = update_stance(new_observations, self.stance)
            plan = create_plan(intent, self.stance, new_observations, self.engine.policy_status(new_state))
            seed = self.engine.repo.get_seed() or 0
            output = render_action_report(seed, result, plan, self.stance)
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
            + "\n\nadvisor: "
            + (", ".join(plan.recommendations) if plan.recommendations else "none")
            + "\nnext: "
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
