from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 3


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def get_meta(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    if not _table_exists(conn, "meta"):
        return default
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default
    return str(row["value"])


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS world_state(
            id INTEGER PRIMARY KEY CHECK (id = 1),
            turn INTEGER NOT NULL,
            treasury INTEGER NOT NULL,
            population INTEGER NOT NULL,
            prosperity REAL NOT NULL,
            stability REAL NOT NULL,
            unrest REAL NOT NULL,
            tech_level REAL NOT NULL,
            last_action_ts TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS market(
            good_id TEXT PRIMARY KEY,
            supply REAL NOT NULL,
            demand REAL NOT NULL,
            price REAL NOT NULL,
            last_price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sectors(
            sector_id TEXT PRIMARY KEY,
            capacity REAL NOT NULL,
            efficiency REAL NOT NULL,
            upkeep REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS active_policies(
            policy_id TEXT PRIMARY KEY,
            remaining_ticks INTEGER NOT NULL,
            cooldown_ticks INTEGER NOT NULL,
            magnitude REAL NOT NULL,
            state_json TEXT NOT NULL DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS history(
            turn INTEGER PRIMARY KEY,
            ts TEXT NOT NULL,
            action TEXT NOT NULL,
            cost INTEGER NOT NULL,
            summary_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events_log(
            turn INTEGER NOT NULL,
            event_id TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            PRIMARY KEY(turn, event_id)
        );

        CREATE TABLE IF NOT EXISTS unlocked_policies(
            policy_id TEXT PRIMARY KEY,
            unlocked_turn INTEGER NOT NULL,
            source TEXT NOT NULL
        );
        """
    )
    set_meta(conn, "language", "de")
    set_meta(conn, "collapse_active", "0")
    set_meta(conn, "collapse_recovery_streak", "0")
    set_meta(conn, "next_unlock_turn", "0")
    set_meta(conn, "last_auto_intel_turn", "-9999")
    set_meta(conn, "schema_version", str(SCHEMA_VERSION))


def migrate_to_v2(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "history"):
        conn.execute(
            """
            CREATE TABLE history(
                turn INTEGER PRIMARY KEY,
                ts TEXT NOT NULL,
                action TEXT NOT NULL,
                cost INTEGER NOT NULL,
                summary_json TEXT NOT NULL
            );
            """
        )
    if not _table_exists(conn, "events_log"):
        conn.execute(
            """
            CREATE TABLE events_log(
                turn INTEGER NOT NULL,
                event_id TEXT NOT NULL,
                summary_json TEXT NOT NULL,
                PRIMARY KEY(turn, event_id)
            );
            """
        )
    if _table_exists(conn, "active_policies") and not _column_exists(conn, "active_policies", "state_json"):
        conn.execute("ALTER TABLE active_policies ADD COLUMN state_json TEXT NOT NULL DEFAULT '{}';")


def _reset_unlocks_to_start_loadout(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM unlocked_policies")
    start_ids = ("TAX_ADJUST", "SUBSIDY_SECTOR", "IMPORT_PROGRAM")
    for policy_id in start_ids:
        conn.execute(
            "INSERT INTO unlocked_policies(policy_id, unlocked_turn, source) VALUES(?, ?, ?)",
            (policy_id, 0, "migration_strict_ramp"),
        )


def migrate_to_v3(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "unlocked_policies"):
        conn.execute(
            """
            CREATE TABLE unlocked_policies(
                policy_id TEXT PRIMARY KEY,
                unlocked_turn INTEGER NOT NULL,
                source TEXT NOT NULL
            );
            """
        )
    _reset_unlocks_to_start_loadout(conn)

    if get_meta(conn, "language", None) is None:
        set_meta(conn, "language", "de")
    if get_meta(conn, "collapse_active", None) is None:
        set_meta(conn, "collapse_active", "0")
    if get_meta(conn, "collapse_recovery_streak", None) is None:
        set_meta(conn, "collapse_recovery_streak", "0")
    if get_meta(conn, "next_unlock_turn", None) is None:
        set_meta(conn, "next_unlock_turn", "0")
    if get_meta(conn, "last_auto_intel_turn", None) is None:
        set_meta(conn, "last_auto_intel_turn", "-9999")


def ensure_schema(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "meta"):
        create_schema(conn)
        return

    raw_version = get_meta(conn, "schema_version", "1")
    version = int(raw_version or "1")

    if version < 2:
        migrate_to_v2(conn)
        version = 2

    if version < 3:
        migrate_to_v3(conn)
        version = 3

    if version < SCHEMA_VERSION:
        create_schema(conn)
        version = SCHEMA_VERSION

    set_meta(conn, "schema_version", str(version))
