from __future__ import annotations

from shinon_os.app_service import AppService
from shinon_os.i18n import t
from shinon_os.view_models import OSResponse, StatusModel


def textual_available() -> bool:
    try:
        import textual  # noqa: F401
    except Exception:
        return False
    return True


def _render_bar(value: float, label: str) -> str:
    clamped = max(0.0, min(1.0, value))
    filled = int(clamped * 10)
    return f"{label}: " + ("#" * filled).ljust(10, ".")


def _render_world_canvas(status: StatusModel | None) -> str:
    if status is None:
        return t("app.error.subsystem")
    lines = [
        f"TURN {status.turn} | VIEW {status.current_view.upper()}",
        _render_bar(status.prosperity, "prosperity"),
        _render_bar(status.stability, "stability"),
        _render_bar(status.unrest, "unrest"),
        _render_bar(status.tech, "tech"),
        _render_bar(status.stance.get("control", 0.0), "control"),
        _render_bar(status.stance.get("growth", 0.0), "growth"),
        _render_bar(status.stance.get("survival", 0.0), "survival"),
    ]
    return "\n".join(lines)


class TextualSession:
    def run(self, service: AppService) -> int:
        try:
            from textual import on
            from textual.app import App, ComposeResult
            from textual.containers import Container, Horizontal, Vertical
            from textual.reactive import reactive
            from textual.screen import Screen
            from textual.widgets import Footer, Header, Input, Static
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError("Textual is not available.") from exc

        class BootScreen(Screen):
            def compose(self) -> ComposeResult:
                yield Container(
                    Static(t("ui.boot.title"), id="boot_title"),
                    id="boot_center",
                )

            def on_mount(self) -> None:
                delay = 0.2 if not service.capabilities.animations_enabled else 3.0
                self.set_timer(delay, lambda: self.app.push_screen(MainScreen()))

        class MainScreen(Screen):
            response: reactive[OSResponse | None] = reactive(None)

            BINDINGS = [
                ("1", "view_dashboard", "Dashboard"),
                ("2", "view_market", "Market"),
                ("3", "view_policies", "Policies"),
                ("4", "view_industry", "Industry"),
                ("5", "view_history", "History"),
                ("6", "view_explain", "Explain"),
                ("?", "show_help", "Help"),
                ("ctrl+q", "app.quit", "Quit"),
                (":", "focus_command", "Cmd"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(show_clock=False)
                with Container(id="frame"):
                    with Horizontal(id="upper"):
                        yield Static(id="world_panel")
                        with Vertical(id="right_stack"):
                            yield Static(t("ui.delta_title"), id="delta_title")
                            yield Static(id="delta_panel")
                            yield Static(t("ui.status_title"), id="status_title")
                            yield Static(id="status_panel")
                    with Vertical(id="chat_zone"):
                        yield Static(t("ui.chat_title"), id="chat_title")
                        yield Static("", id="chat_log")
                        yield Input(placeholder=t("ui.input_placeholder"), id="chat_input")
                yield Footer()

            def on_mount(self) -> None:
                self._chat_lines: list[str] = []
                service.bootstrap()
                self._refresh_labels()
                self._update_view("dashboard")
                if service.capabilities.animations_enabled and not service.capabilities.safe_mode:
                    self.set_interval(1.0, self._ambient_refresh)

            def _refresh_labels(self) -> None:
                self.query_one("#delta_title", Static).update(t("ui.delta_title"))
                self.query_one("#status_title", Static).update(t("ui.status_title"))
                self.query_one("#chat_title", Static).update(t("ui.chat_title"))
                self.query_one("#chat_input", Input).placeholder = t("ui.input_placeholder")

            def _ambient_refresh(self) -> None:
                if self.response and not self.response.turn_advanced:
                    self._render_status(self.response.status)

            def _append_chat(self, text: str) -> None:
                log = self.query_one("#chat_log", Static)
                self._chat_lines.append(text)
                log.update("\n".join(self._chat_lines))

            def _render_status(self, status: StatusModel | None) -> None:
                self.query_one("#world_panel", Static).update(_render_world_canvas(status))
                if status:
                    self.query_one("#status_panel", Static).update(
                        f"treasury: {status.treasury}\npop: {status.population}\nprosperity: {status.prosperity:.2f}"
                    )

            def _apply_response(self, resp: OSResponse) -> None:
                self.response = resp
                self._append_chat(resp.message)
                self._render_status(resp.status)
                if resp.events:
                    self.query_one("#delta_panel", Static).update(" | ".join(resp.events))
                else:
                    self.query_one("#delta_panel", Static).update(t("ui.no_events"))
                if resp.locale_changed:
                    self._refresh_labels()
                if resp.turn_advanced and service.capabilities.animations_enabled:
                    self.add_class("fx-turn")
                    self.set_timer(0.3, lambda: self.remove_class("fx-turn"))
                if resp.should_quit:
                    self.app.exit()

            def _update_view(self, view: str) -> None:
                resp = service.get_view(view)
                self._apply_response(resp)

            def _handle_command(self, text: str) -> None:
                resp = service.handle_input(text)
                self._apply_response(resp)

            @on(Input.Submitted, "#chat_input")
            def on_input_submitted(self, event: Input.Submitted) -> None:
                text = event.value.strip()
                event.input.value = ""
                if not text:
                    return
                if text.startswith(":"):
                    cmd = text[1:]
                    self._handle_command(cmd)
                else:
                    self._handle_command(text)

            def action_view_dashboard(self) -> None:
                self._update_view("dashboard")

            def action_view_market(self) -> None:
                self._update_view("market")

            def action_view_policies(self) -> None:
                self._update_view("policies")

            def action_view_industry(self) -> None:
                self._update_view("industry")

            def action_view_history(self) -> None:
                self._update_view("history")

            def action_view_explain(self) -> None:
                self._update_view("explain prices")

            def action_show_help(self) -> None:
                self._append_chat(t("ui.help.short"))

            def action_focus_command(self) -> None:
                self.query_one("#chat_input", Input).focus()
                self.query_one("#chat_input", Input).value = ":"

        class ShinonTextualApp(App):
            CSS = """
            Screen { background: #000000; color: #d0f4ff; }
            #boot_center { align: center middle; height: 100%; background: #000000; }
            #boot_title { content-align: center middle; color: #6cf0ff; text-style: bold; }
            #frame { height: 1fr; padding: 1; }
            #upper { height: 2fr; }
            #world_panel { border: solid #0ff; padding: 1; width: 3fr; }
            #right_stack { width: 1fr; border: solid #0af; padding: 1; }
            #delta_panel, #status_panel { height: 1fr; }
            #chat_zone { height: 1fr; border: solid #0f0; padding: 1; }
            #chat_log { height: 1fr; }
            #chat_input { dock: bottom; }
            .fx-turn { background: #102030; }
            """

            def on_mount(self) -> None:
                self.push_screen(BootScreen())

        ShinonTextualApp().run()
        return 0
