from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 2


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
        """
    )
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


def ensure_schema(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "meta"):
        create_schema(conn)
        return

    raw_version = get_meta(conn, "schema_version", "1")
    version = int(raw_version or "1")

    if version < 2:
        migrate_to_v2(conn)
        version = 2

    if version < SCHEMA_VERSION:
        create_schema(conn)
        version = SCHEMA_VERSION

    set_meta(conn, "schema_version", str(version))
