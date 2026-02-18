from __future__ import annotations

import sqlite3
from pathlib import Path

from shinon_os.persistence.repo import StateRepository
from shinon_os.sim.worldgen import load_data


def test_migration_from_v1_to_v3(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.sqlite3"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        INSERT INTO meta(key, value) VALUES ('schema_version', '1');
        INSERT INTO meta(key, value) VALUES ('seed', '123');
        INSERT INTO meta(key, value) VALUES ('created_at', '2026-02-18T00:00:00+00:00');

        CREATE TABLE world_state(
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

        CREATE TABLE market(
            good_id TEXT PRIMARY KEY,
            supply REAL NOT NULL,
            demand REAL NOT NULL,
            price REAL NOT NULL,
            last_price REAL NOT NULL
        );

        CREATE TABLE sectors(
            sector_id TEXT PRIMARY KEY,
            capacity REAL NOT NULL,
            efficiency REAL NOT NULL,
            upkeep REAL NOT NULL
        );

        CREATE TABLE active_policies(
            policy_id TEXT PRIMARY KEY,
            remaining_ticks INTEGER NOT NULL,
            cooldown_ticks INTEGER NOT NULL,
            magnitude REAL NOT NULL
        );
        """
    )
    conn.execute(
        """
        INSERT INTO world_state(id, turn, treasury, population, prosperity, stability, unrest, tech_level, last_action_ts)
        VALUES(1, 0, 10000, 100000, 50.0, 50.0, 10.0, 20.0, '2026-02-18T00:00:00+00:00')
        """
    )
    conn.execute(
        "INSERT INTO market(good_id, supply, demand, price, last_price) VALUES ('grain', 100, 90, 4.0, 4.0)"
    )
    conn.execute(
        "INSERT INTO sectors(sector_id, capacity, efficiency, upkeep) VALUES ('agriculture', 100, 0.8, 900)"
    )
    conn.commit()
    conn.close()

    repo = StateRepository(db_path)
    try:
        migrated = repo.conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        assert migrated is not None
        assert migrated[0] == "3"

        cols = [row[1] for row in repo.conn.execute("PRAGMA table_info(active_policies)").fetchall()]
        assert "state_json" in cols
        unlocked_cols = [row[1] for row in repo.conn.execute("PRAGMA table_info(unlocked_policies)").fetchall()]
        assert "policy_id" in unlocked_cols

        bundle = load_data()
        state = repo.load_state(bundle.sector_io_defs())
        assert state.world.turn == 0
        assert repo.get_language() == "de"
    finally:
        repo.close()
