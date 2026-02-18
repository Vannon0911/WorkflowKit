from __future__ import annotations

from shinon_os.app_service import AppOptions, AppService


def test_no_anim_disables_animations_and_completes_boot() -> None:
    service = AppService(AppOptions(no_anim=True))
    assert service.capabilities.animations_enabled is False
    resp = service.bootstrap()
    assert resp.turn_advanced is False
    assert service.app.boot_sequence_model().status == "DONE"
    service.shutdown()
