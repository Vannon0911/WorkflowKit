from __future__ import annotations

import json
import logging
from pathlib import Path

from shinon_os.util.paths import package_data_dir

_LOG = logging.getLogger("shinon_os.i18n")
_SUPPORTED = {"de", "en"}
_active_lang = "de"
_cache: dict[str, dict[str, str]] = {}
_warned_missing: set[tuple[str, str]] = set()


def _locale_path(lang: str) -> Path:
    return package_data_dir() / f"{lang}.json"


def _load_locale(lang: str) -> dict[str, str]:
    if lang in _cache:
        return _cache[lang]
    path = _locale_path(lang)
    if not path.exists():
        _cache[lang] = {}
        return _cache[lang]
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    _cache[lang] = {str(k): str(v) for k, v in raw.items()}
    return _cache[lang]


def get_lang() -> str:
    return _active_lang


def set_lang(code: str) -> str:
    global _active_lang
    normalized = (code or "").strip().lower()
    if normalized not in _SUPPORTED:
        normalized = "en"
    _active_lang = normalized
    return _active_lang


def t(key: str, **kwargs: object) -> str:
    lang = get_lang()
    active = _load_locale(lang)
    text = active.get(key)
    if text is None:
        fallback = _load_locale("en").get(key)
        if fallback is None:
            miss = (lang, key)
            if miss not in _warned_missing:
                _warned_missing.add(miss)
                _LOG.warning("missing i18n key", extra={"lang": lang, "key": key})
            return f"[missing:{key}]"
        text = fallback
        miss = (lang, key)
        if miss not in _warned_missing:
            _warned_missing.add(miss)
            _LOG.warning("missing i18n key in active locale", extra={"lang": lang, "key": key})
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
