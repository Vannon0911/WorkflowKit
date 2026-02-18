from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp


def _enact(app: ShinonApp, policy_id: str, magnitude: float, target: str | None = None) -> None:
    result = app.engine.advance_turn(policy_id=policy_id, magnitude=magnitude, target=target)
    assert result.ok, result.message


def test_unlock_ramp_and_cooldown(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "unlocks.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=123)
        state = app.engine.load_state()
        assert state.unlocked_policies == {"TAX_ADJUST", "SUBSIDY_SECTOR", "IMPORT_PROGRAM"}

        _enact(app, "TAX_ADJUST", 0.05)
        _enact(app, "SUBSIDY_SECTOR", 1.0, "agriculture")
        _enact(app, "IMPORT_PROGRAM", 10.0, "grain")
        _enact(app, "FUND_RESEARCH", 1.0)
        _enact(app, "SECURITY_BUDGET", 0.5)
        _enact(app, "RATIONING", 0.5)

        state = app.engine.load_state()
        assert "PRICE_STABILIZER" in state.unlocked_policies
        assert app.engine.repo.get_int_meta("next_unlock_turn", 0) == 9
        assert "LOGISTICS_PUSH" not in state.unlocked_policies

        _enact(app, "WORK_HOURS_REFORM", 0.5)
        _enact(app, "BUILD_INFRA", 1.0, "industry")
        state = app.engine.load_state()
        assert "LOGISTICS_PUSH" not in state.unlocked_policies

        _enact(app, "TAX_ADJUST", 0.05)
        state = app.engine.load_state()
        assert "LOGISTICS_PUSH" in state.unlocked_policies
    finally:
        app.shutdown()


def test_collapse_and_recovery_toggle_emergency_policies(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "collapse.sqlite3", log_dir=tmp_path / "logs")
    try:
        app.start_new_game(seed=44)

        state = app.engine.load_state()
        state.world.treasury = 1500
        for sector in state.sectors.values():
            sector.upkeep = 3000.0
        app.engine.repo.save_state(state)

        _enact(app, "TAX_ADJUST", 0.05)
        assert app.engine.repo.get_bool_meta("collapse_active", False) is True

        state = app.engine.load_state()
        status_rows = {str(row["id"]): str(row["status"]) for row in app.engine.policy_status(state)}
        assert status_rows["SOS_CREDIT"] in {"available", "active", "cooldown"}
        assert status_rows["RATIONING_PLUS"] in {"available", "active", "cooldown"}

        state = app.engine.load_state()
        state.world.treasury = 100000
        for sector in state.sectors.values():
            sector.upkeep = 0.0
        state.active_policies = {}
        app.engine.repo.save_state(state)

        _enact(app, "SOS_CREDIT", 1.0)
        state = app.engine.load_state()
        state.active_policies = {}
        app.engine.repo.save_state(state)
        _enact(app, "RATIONING_PLUS", 1.0)

        assert app.engine.repo.get_bool_meta("collapse_active", False) is False
        state = app.engine.load_state()
        status_rows = {str(row["id"]): str(row["status"]) for row in app.engine.policy_status(state)}
        assert status_rows["SOS_CREDIT"] == "locked"
        assert status_rows["RATIONING_PLUS"] == "locked"
    finally:
        app.shutdown()
