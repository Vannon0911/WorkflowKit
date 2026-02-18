from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService


def test_view_models_complete(tmp_path: Path) -> None:
    app = ShinonApp(db_path=tmp_path / "vm.sqlite3", log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    service.app.start_new_game(seed=123)

    for view_id in ["dashboard", "market", "policies", "industry", "history", "explain prices"]:
        resp = service.get_view(view_id)
        assert resp.view_model is not None
        assert resp.status is not None
        assert resp.turn_advanced is False
    service.shutdown()
