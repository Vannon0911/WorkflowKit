from __future__ import annotations

from pathlib import Path

from shinon_os.app import ShinonApp
from shinon_os.app_service import AppOptions, AppService
from shinon_os.i18n import set_lang, t


def test_locale_fallback_to_en_for_missing_key() -> None:
    set_lang("de")
    assert t("test.only_en") == "Only EN value"


def test_locale_missing_key_marker() -> None:
    set_lang("de")
    key = "missing.key.zz"
    assert t(key) == f"[missing:{key}]"


def test_lang_command_persists_to_db(tmp_path: Path) -> None:
    db_path = tmp_path / "lang.sqlite3"
    app = ShinonApp(db_path=db_path, log_dir=tmp_path / "logs")
    service = AppService(AppOptions(no_anim=True), app=app)
    service.app.start_new_game(seed=42)
    response = service.handle_input("lang en")
    assert response.turn_advanced is False
    assert response.locale_changed is True
    service.shutdown()

    app2 = ShinonApp(db_path=db_path, log_dir=tmp_path / "logs2")
    try:
        assert app2.repo.get_language() == "en"
    finally:
        app2.shutdown()
