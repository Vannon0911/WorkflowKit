from __future__ import annotations

import time
from pathlib import Path

from shinon_os.core.kernel import ShinonKernel
from shinon_os.core.types import BootSequenceModel, KernelResponse
from shinon_os.persistence.repo import StateRepository
from shinon_os.sim.engine import SimulationEngine
from shinon_os.sim.worldgen import DataBundle, load_data
from shinon_os.util.logging_setup import JsonlRotatingLogger
from shinon_os.util.paths import default_db_path, default_log_dir


class ShinonApp:
    def __init__(self, db_path: Path | None = None, data_dir: Path | None = None, log_dir: Path | None = None) -> None:
        self.db_path = db_path or default_db_path()
        self.bundle: DataBundle = load_data(data_dir=data_dir)
        self.logger = JsonlRotatingLogger(log_dir or default_log_dir())
        self.repo = StateRepository(self.db_path)
        self.engine = SimulationEngine(bundle=self.bundle, repo=self.repo, logger=self.logger)
        self.kernel = ShinonKernel(engine=self.engine, logger=self.logger)
        self._boot_model = BootSequenceModel(
            stages=[
                "Kernel init",
                "DB mount / migration check",
                "Subsystem checks",
                "SHINON online",
            ],
            durations_ms=[650, 650, 700, 700],
            status="PENDING",
        )

    def has_existing_game(self) -> bool:
        return self.repo.has_game()

    def start_new_game(self, seed: int) -> None:
        self.engine.new_game(seed=seed)
        self.kernel.current_view = "dashboard"
        self.kernel.last_world_snapshot = None

    def load_game(self) -> None:
        self.engine.ensure_game(seed=42)
        self.kernel.current_view = "dashboard"
        self.kernel.last_world_snapshot = None

    def process_command(self, command: str) -> KernelResponse:
        return self.kernel.handle(command)

    def current_turn(self) -> int:
        return self.engine.load_state().world.turn

    def snapshot(self) -> dict[str, object]:
        return self.engine.snapshot()

    def boot_sequence_model(self) -> BootSequenceModel:
        return BootSequenceModel(
            stages=list(self._boot_model.stages),
            durations_ms=list(self._boot_model.durations_ms),
            status=self._boot_model.status,
        )

    def run_boot_sequence(self, emit: callable, sleep_fn: callable | None = None) -> None:
        sleeper = sleep_fn or time.sleep
        self._boot_model.status = "RUNNING"
        for stage, duration_ms in zip(self._boot_model.stages, self._boot_model.durations_ms):
            emit(f"[BOOT] {stage} ...")
            sleeper(duration_ms / 1000.0)
        self._boot_model.status = "DONE"
        emit("[BOOT] SHINON kernel ready.")

    def shutdown(self) -> None:
        self.repo.close()


def _parse_seed(raw_seed: str) -> int:
    raw_seed = raw_seed.strip()
    if not raw_seed:
        return 42
    try:
        return int(raw_seed)
    except ValueError:
        return 42


def run_app(ui_mode: str | None = None, no_anim: bool = False, safe_ui: bool = False) -> None:
    from shinon_os.app_service import AppOptions, AppService
    from shinon_os.ui.factory import create_ui

    service = AppService(AppOptions(ui_mode=ui_mode, no_anim=no_anim, safe_ui=safe_ui))
    run_error: BaseException | None = None
    try:
        session = create_ui(service)
        session.run(service)
    except BaseException as exc:
        run_error = exc
        service.finalize_transcript_error(exc)
        raise
    finally:
        if run_error is None:
            service.finalize_transcript_ok()
        service.shutdown()


def select_profile(app: ShinonApp, ask_input: callable, emit: callable) -> None:
    emit(f"Save location: {app.db_path}")
    if app.has_existing_game():
        choice = ask_input("[N]ew / [L]oad > ").strip().lower()
        if choice.startswith("l"):
            app.load_game()
            emit("Loaded existing simulation state.")
            return
    seed = _parse_seed(ask_input("New game seed (default 42): "))
    app.start_new_game(seed=seed)
    emit(f"Started new game with seed {seed}.")
