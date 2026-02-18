from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from shinon_os.app import ShinonApp
from shinon_os.core import intents
from shinon_os.view_models import (
    CapabilityRegistry,
    DashboardVM,
    ExplainVM,
    HistoryRow,
    HistoryVM,
    IndustryRow,
    IndustryVM,
    MarketRow,
    MarketVM,
    MenuModel,
    OSResponse,
    PoliciesVM,
    PolicyRow,
    StatusModel,
)


@dataclass
class AppOptions:
    ui_mode: str | None = None
    no_anim: bool = False
    safe_ui: bool = False


def _textual_available() -> bool:
    try:
        from shinon_os.ui.textual_app import textual_available

        return textual_available()
    except Exception:
        return False


class AppService:
    def __init__(self, options: AppOptions, app: ShinonApp | None = None) -> None:
        self.options = options
        self.app = app or ShinonApp()
        self.capabilities = CapabilityRegistry(
            textual_available=_textual_available(),
            animations_enabled=not options.no_anim,
            safe_mode=options.safe_ui,
            palette="oled",
        )

    def shutdown(self) -> None:
        self.app.shutdown()

    def bootstrap(self) -> OSResponse:
        try:
            if self.capabilities.animations_enabled:
                self.app.run_boot_sequence(emit=lambda msg: self.app.logger.debug({"where": "boot", "msg": msg}))
            else:
                model = self.app.boot_sequence_model()
                for stage in model.stages:
                    self.app.logger.debug({"where": "boot", "msg": f"[BOOT] {stage} ...", "skipped": True})
                # ensure DONE status
                self.app.run_boot_sequence(emit=lambda _: None, sleep_fn=lambda _: None)
        except Exception as exc:  # pragma: no cover - defensive
            self.app.logger.error({"where": "bootstrap", "error": str(exc)})
            return self._os_error("Subsystem not available")
        return OSResponse(
            message="Boot complete",
            view="status",
            view_model=None,
            status=self.get_status(),
            menu=self.get_menu(),
            capability=self.capabilities,
            turn_advanced=False,
            should_quit=False,
        )

    def get_menu(self) -> MenuModel:
        return MenuModel(
            commands=[
                "dashboard",
                "market",
                "policies",
                "industry",
                "history",
                "explain <topic>",
                "enact <policy> [magnitude] [target]",
                "quit",
            ],
            hotkeys=["1..6 views", "?: help", "Ctrl+Q: quit", ":cmd palette"],
            help="Views do not advance turns; actions advance exactly one turn.",
        )

    def get_status(self) -> StatusModel | None:
        try:
            state = self.app.engine.load_state()
        except Exception:
            return None
        stance = self.app.kernel.stance
        return StatusModel(
            turn=state.world.turn,
            current_view=self.app.kernel.current_view,
            treasury=state.world.treasury,
            population=state.world.population,
            prosperity=state.world.prosperity,
            stability=state.world.stability,
            unrest=state.world.unrest,
            tech=state.world.tech_level,
            stance={
                "control": stance.control,
                "growth": stance.growth,
                "survival": stance.survival,
                "urgency": stance.urgency,
                "confidence": stance.confidence,
                "trust_in_operator": stance.trust_in_operator,
            },
        )

    def _dashboard_vm(self) -> DashboardVM:
        state = self.app.engine.load_state()
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
        return DashboardVM(shortages=shortages, top_movers=movers, active_policies=active_rows)

    def _market_vm(self) -> MarketVM:
        state = self.app.engine.load_state()
        rows: list[MarketRow] = []
        for good_id, item in sorted(state.market.items()):
            delta = ((item.price - item.last_price) / item.last_price * 100.0) if item.last_price > 0 else 0.0
            rows.append(
                MarketRow(
                    good=good_id,
                    supply=item.supply,
                    demand=item.demand,
                    price=item.price,
                    delta_pct=delta,
                )
            )
        return MarketVM(rows=rows)

    def _policies_vm(self) -> PoliciesVM:
        state = self.app.engine.load_state()
        rows = [
            PolicyRow(
                policy_id=str(row["id"]),
                status=str(row["status"]),
                remaining_ticks=int(row["remaining_ticks"]),
                cooldown_ticks=int(row["cooldown_ticks"]),
                label=str(row["label"]),
            )
            for row in self.app.engine.policy_status(state)
        ]
        return PoliciesVM(rows=rows)

    def _industry_vm(self) -> IndustryVM:
        state = self.app.engine.load_state()
        rows = [
            IndustryRow(sector_id=sector_id, capacity=sector.capacity, efficiency=sector.efficiency, upkeep=sector.upkeep)
            for sector_id, sector in sorted(state.sectors.items())
        ]
        return IndustryVM(rows=rows)

    def _history_vm(self) -> HistoryVM:
        rows = []
        for row in self.app.engine.repo.history(limit=10):
            summary = row["summary"]
            rows.append(
                HistoryRow(
                    turn=int(row["turn"]),
                    action=str(row["action"]),
                    cost=float(row["cost"]),
                    inflation=float(summary.get("inflation", 0.0)),
                    events=list(summary.get("events", [])),
                )
            )
        return HistoryVM(rows=rows)

    def _explain_vm(self, topic: str) -> ExplainVM:
        normalized = topic.strip().lower()
        if normalized in {"price", "prices"}:
            text = (
                "prices: demand/supply ratio is damped into [0.5, 2.0], then applied via lerp with k_demand. "
                "shortages: supply < demand*(1-shortage_threshold) raises unrest pressure and lowers prosperity."
            )
        elif normalized in {"shortage", "shortages"}:
            text = "shortages increase social risk. SHINON tracks shortage_risk and pushes CONTROL or SURVIVAL stance."
        elif normalized.startswith("policy "):
            policy_id = normalized.split(" ", 1)[1].upper()
            definition = self.app.engine.bundle.policies.get(policy_id)
            text = f"{policy_id}: {definition.description}" if definition else "unknown policy"
        else:
            text = "topics: explain prices | explain shortages | explain policy <POLICY_ID>"
        return ExplainVM(topic=topic or "general", text=text)

    def get_view(self, view_id: str) -> OSResponse:
        view_id_normalized = view_id.strip().lower()
        vm = None
        if view_id_normalized in {"dashboard", "dash"}:
            vm = self._dashboard_vm()
        elif view_id_normalized == "market":
            vm = self._market_vm()
        elif view_id_normalized == "policies":
            vm = self._policies_vm()
        elif view_id_normalized == "industry":
            vm = self._industry_vm()
        elif view_id_normalized == "history":
            vm = self._history_vm()
        else:
            vm = self._explain_vm(view_id_normalized)
        return OSResponse(
            message="VIEW",
            view=view_id_normalized,
            view_model=vm,
            status=self.get_status(),
            menu=self.get_menu(),
            capability=self.capabilities,
            turn_advanced=False,
            should_quit=False,
        )

    def get_help(self) -> OSResponse:
        return OSResponse(
            message="SHINON help: 1..6 switch views, :command executes, actions advance one turn, views do not.",
            view="help",
            view_model=None,
            status=self.get_status(),
            menu=self.get_menu(),
            capability=self.capabilities,
            turn_advanced=False,
            should_quit=False,
        )

    def handle_input(self, text: str) -> OSResponse:
        raw = text or ""
        try:
            response = self.app.process_command(raw)
            self.app.logger.debug({"where": "app_service.handle", "raw": raw, "turn_advanced": response.turn_advanced})
            view_model = self._select_view_model(response.current_view, raw)
            friendly_message = response.output
            raw_lower = raw.strip().lower()
            if (
                not response.turn_advanced
                and response.chat_turn is not None
                and response.chat_turn.recognized_intent == intents.HELP
                and raw_lower not in {"h", "help", "?"}
            ):
                friendly_message = "Subsystem not available"
            return OSResponse(
                message=friendly_message,
                view=response.current_view,
                view_model=view_model,
                status=self.get_status(),
                menu=self.get_menu(),
                capability=self.capabilities,
                turn_advanced=response.turn_advanced,
                should_quit=response.should_quit,
                events=response.chat_turn.events if response.chat_turn else [],
            )
        except Exception as exc:  # pragma: no cover - defensive
            self.app.logger.error({"where": "app_service.handle.error", "raw": raw, "error": str(exc)})
            return self._os_error("Subsystem not available")

    def _select_view_model(self, intent_kind_or_view: str, raw: str) -> object | None:
        kind = intent_kind_or_view or ""
        low = kind.lower()
        if low in {intents.VIEW_DASH.lower(), "dashboard", "view_dash"}:
            return self._dashboard_vm()
        if low in {intents.VIEW_MARKET.lower(), "market", "view_market"}:
            return self._market_vm()
        if low in {intents.VIEW_POLICIES.lower(), "policies", "view_policies"}:
            return self._policies_vm()
        if low in {intents.VIEW_INDUSTRY.lower(), "industry", "view_industry"}:
            return self._industry_vm()
        if low in {intents.VIEW_HISTORY.lower(), "history", "view_history"}:
            return self._history_vm()
        if low == intents.EXPLAIN.lower():
            topic = raw.split(" ", 1)[1] if " " in raw else "general"
            return self._explain_vm(topic)
        return None

    def _os_error(self, message: str) -> OSResponse:
        return OSResponse(
            message=message,
            view="error",
            view_model=None,
            status=self.get_status(),
            menu=self.get_menu(),
            capability=self.capabilities,
            turn_advanced=False,
            should_quit=False,
        )
