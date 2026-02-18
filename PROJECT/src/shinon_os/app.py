from __future__ import annotations

from pathlib import Path

from shinon_os.cli.io import print_block, safe_input
from shinon_os.core.kernel import ShinonKernel
from shinon_os.core.types import KernelResponse
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


def run_cli() -> None:
    app = ShinonApp()
    print_block("SHINON kernel booting...")
    print_block(f"Save location: {app.db_path}")
    try:
        if app.has_existing_game():
            choice = safe_input("[N]ew / [L]oad > ").strip().lower()
            if choice.startswith("l"):
                app.load_game()
                print_block("Loaded existing simulation state.")
            else:
                seed = _parse_seed(safe_input("New game seed (default 42): "))
                app.start_new_game(seed=seed)
                print_block(f"Started new game with seed {seed}.")
        else:
            seed = _parse_seed(safe_input("New game seed (default 42): "))
            app.start_new_game(seed=seed)
            print_block(f"Started new game with seed {seed}.")

        first = app.process_command("dashboard")
        print_block(first.output)
        while True:
            raw = safe_input("shinon> ")
            response = app.process_command(raw)
            print_block(response.output)
            if response.should_quit:
                break
    finally:
        app.shutdown()
