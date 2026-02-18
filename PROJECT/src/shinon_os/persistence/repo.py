from __future__ import annotations

import json
from pathlib import Path

from shinon_os.persistence.db import connect
from shinon_os.persistence.schema import ensure_schema, get_meta, set_meta
from shinon_os.sim.model import GameState, MarketGood, PolicyRuntime, SectorState, WorldState
from shinon_os.util.timeutil import utc_now_iso

START_LOADOUT = ("TAX_ADJUST", "SUBSIDY_SECTOR", "IMPORT_PROGRAM")


class StateRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = connect(db_path)
        ensure_schema(self.conn)

    def close(self) -> None:
        self.conn.close()

    def has_game(self) -> bool:
        row = self.conn.execute("SELECT 1 FROM world_state WHERE id = 1").fetchone()
        return row is not None

    def get_seed(self) -> int | None:
        raw = get_meta(self.conn, "seed", None)
        if raw is None:
            return None
        return int(raw)

    def get_language(self) -> str:
        return str(get_meta(self.conn, "language", "de") or "de")

    def set_language(self, code: str) -> None:
        normalized = (code or "").strip().lower()
        with self.conn:
            set_meta(self.conn, "language", "de" if normalized not in {"de", "en"} else normalized)

    def get_str_meta(self, key: str, default: str = "") -> str:
        raw = get_meta(self.conn, key, default)
        return str(raw if raw is not None else default)

    def set_str_meta(self, key: str, value: str) -> None:
        with self.conn:
            set_meta(self.conn, key, str(value))

    def get_int_meta(self, key: str, default: int = 0) -> int:
        raw = get_meta(self.conn, key, None)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    def set_int_meta(self, key: str, value: int) -> None:
        with self.conn:
            set_meta(self.conn, key, str(int(value)))

    def get_bool_meta(self, key: str, default: bool = False) -> bool:
        return self.get_int_meta(key, 1 if default else 0) != 0

    def set_bool_meta(self, key: str, value: bool) -> None:
        self.set_int_meta(key, 1 if value else 0)

    def list_unlocked_policies(self) -> set[str]:
        rows = self.conn.execute("SELECT policy_id FROM unlocked_policies ORDER BY policy_id").fetchall()
        return {str(row["policy_id"]) for row in rows}

    def unlocked_policy_rows(self) -> list[dict[str, object]]:
        rows = self.conn.execute(
            "SELECT policy_id, unlocked_turn, source FROM unlocked_policies ORDER BY unlocked_turn, policy_id"
        ).fetchall()
        result: list[dict[str, object]] = []
        for row in rows:
            result.append(
                {
                    "policy_id": str(row["policy_id"]),
                    "unlocked_turn": int(row["unlocked_turn"]),
                    "source": str(row["source"]),
                }
            )
        return result

    def replace_unlocked_policies(self, policy_ids: set[str], turn: int, source: str = "reset") -> None:
        with self.conn:
            self.conn.execute("DELETE FROM unlocked_policies")
            for policy_id in sorted(policy_ids):
                self.conn.execute(
                    "INSERT INTO unlocked_policies(policy_id, unlocked_turn, source) VALUES(?, ?, ?)",
                    (policy_id, int(turn), source),
                )

    def unlock_policy(self, policy_id: str, turn: int, source: str = "rule") -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO unlocked_policies(policy_id, unlocked_turn, source)
                VALUES(?, ?, ?)
                ON CONFLICT(policy_id) DO UPDATE SET
                    unlocked_turn = excluded.unlocked_turn,
                    source = excluded.source
                """,
                (policy_id, int(turn), source),
            )

    def trailing_cashflow(self, window: int, include_current: float = 0.0) -> float:
        if window <= 0:
            return 0.0
        rows = self.history(limit=max(0, window - 1))
        total = float(include_current)
        for row in rows:
            summary = row.get("summary", {})
            total += float(summary.get("net_cashflow", 0.0))
        return total

    def init_new_game(self, seed: int, state: GameState) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM world_state")
            self.conn.execute("DELETE FROM market")
            self.conn.execute("DELETE FROM sectors")
            self.conn.execute("DELETE FROM active_policies")
            self.conn.execute("DELETE FROM history")
            self.conn.execute("DELETE FROM events_log")
            self.conn.execute("DELETE FROM unlocked_policies")

            set_meta(self.conn, "seed", str(seed))
            set_meta(self.conn, "created_at", utc_now_iso())
            set_meta(self.conn, "language", "de")
            set_meta(self.conn, "collapse_active", "0")
            set_meta(self.conn, "collapse_recovery_streak", "0")
            set_meta(self.conn, "next_unlock_turn", "0")
            set_meta(self.conn, "last_auto_intel_turn", "-9999")
            set_meta(self.conn, "last_intel_hint_id", "")

            self.conn.execute(
                """
                INSERT INTO world_state(
                    id, turn, treasury, population, prosperity, stability, unrest, tech_level, last_action_ts
                ) VALUES(1, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.world.turn,
                    state.world.treasury,
                    state.world.population,
                    state.world.prosperity,
                    state.world.stability,
                    state.world.unrest,
                    state.world.tech_level,
                    state.world.last_action_ts,
                ),
            )

            for good in state.market.values():
                self.conn.execute(
                    """
                    INSERT INTO market(good_id, supply, demand, price, last_price)
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (good.good_id, good.supply, good.demand, good.price, good.last_price),
                )

            for sector in state.sectors.values():
                self.conn.execute(
                    """
                    INSERT INTO sectors(sector_id, capacity, efficiency, upkeep)
                    VALUES(?, ?, ?, ?)
                    """,
                    (sector.sector_id, sector.capacity, sector.efficiency, sector.upkeep),
                )

            for policy_id in START_LOADOUT:
                self.conn.execute(
                    "INSERT INTO unlocked_policies(policy_id, unlocked_turn, source) VALUES(?, ?, ?)",
                    (policy_id, 0, "new_game"),
                )

    def load_state(self, sector_io_defs: dict[str, dict[str, dict[str, float]]]) -> GameState:
        world_row = self.conn.execute("SELECT * FROM world_state WHERE id = 1").fetchone()
        if world_row is None:
            raise RuntimeError("No saved world_state found.")

        world = WorldState(
            turn=int(world_row["turn"]),
            treasury=int(world_row["treasury"]),
            population=int(world_row["population"]),
            prosperity=float(world_row["prosperity"]),
            stability=float(world_row["stability"]),
            unrest=float(world_row["unrest"]),
            tech_level=float(world_row["tech_level"]),
            last_action_ts=str(world_row["last_action_ts"]),
        )

        market_rows = self.conn.execute("SELECT * FROM market ORDER BY good_id").fetchall()
        market: dict[str, MarketGood] = {}
        for row in market_rows:
            market[row["good_id"]] = MarketGood(
                good_id=row["good_id"],
                supply=float(row["supply"]),
                demand=float(row["demand"]),
                price=float(row["price"]),
                last_price=float(row["last_price"]),
            )

        sector_rows = self.conn.execute("SELECT * FROM sectors ORDER BY sector_id").fetchall()
        sectors: dict[str, SectorState] = {}
        for row in sector_rows:
            io_def = sector_io_defs.get(row["sector_id"], {"inputs": {}, "outputs": {}})
            sectors[row["sector_id"]] = SectorState(
                sector_id=row["sector_id"],
                capacity=float(row["capacity"]),
                efficiency=float(row["efficiency"]),
                upkeep=float(row["upkeep"]),
                inputs=dict(io_def.get("inputs", {})),
                outputs=dict(io_def.get("outputs", {})),
            )

        policy_rows = self.conn.execute("SELECT * FROM active_policies ORDER BY policy_id").fetchall()
        active_policies: dict[str, PolicyRuntime] = {}
        for row in policy_rows:
            active_policies[row["policy_id"]] = PolicyRuntime(
                policy_id=row["policy_id"],
                remaining_ticks=int(row["remaining_ticks"]),
                cooldown_ticks=int(row["cooldown_ticks"]),
                magnitude=float(row["magnitude"]),
                state=json.loads(str(row["state_json"])),
            )

        unlocked_rows = self.conn.execute(
            "SELECT policy_id FROM unlocked_policies ORDER BY policy_id"
        ).fetchall()
        unlocked_policies = {str(row["policy_id"]) for row in unlocked_rows}

        return GameState(
            world=world,
            market=market,
            sectors=sectors,
            unlocked_policies=unlocked_policies,
            active_policies=active_policies,
        )

    def save_state(self, state: GameState) -> None:
        with self.conn:
            self.conn.execute(
                """
                UPDATE world_state
                SET turn = ?, treasury = ?, population = ?, prosperity = ?, stability = ?, unrest = ?, tech_level = ?, last_action_ts = ?
                WHERE id = 1
                """,
                (
                    state.world.turn,
                    state.world.treasury,
                    state.world.population,
                    state.world.prosperity,
                    state.world.stability,
                    state.world.unrest,
                    state.world.tech_level,
                    state.world.last_action_ts,
                ),
            )

            for good in state.market.values():
                self.conn.execute(
                    """
                    INSERT INTO market(good_id, supply, demand, price, last_price)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(good_id) DO UPDATE SET
                        supply = excluded.supply,
                        demand = excluded.demand,
                        price = excluded.price,
                        last_price = excluded.last_price
                    """,
                    (good.good_id, good.supply, good.demand, good.price, good.last_price),
                )

            for sector in state.sectors.values():
                self.conn.execute(
                    """
                    INSERT INTO sectors(sector_id, capacity, efficiency, upkeep)
                    VALUES(?, ?, ?, ?)
                    ON CONFLICT(sector_id) DO UPDATE SET
                        capacity = excluded.capacity,
                        efficiency = excluded.efficiency,
                        upkeep = excluded.upkeep
                    """,
                    (sector.sector_id, sector.capacity, sector.efficiency, sector.upkeep),
                )

            self.conn.execute("DELETE FROM active_policies")
            for runtime in state.active_policies.values():
                self.conn.execute(
                    """
                    INSERT INTO active_policies(policy_id, remaining_ticks, cooldown_ticks, magnitude, state_json)
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        runtime.policy_id,
                        runtime.remaining_ticks,
                        runtime.cooldown_ticks,
                        runtime.magnitude,
                        json.dumps(runtime.state, ensure_ascii=True),
                    ),
                )

    def append_history(self, turn: int, action: str, cost: int, summary: dict[str, object]) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO history(turn, ts, action, cost, summary_json)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(turn) DO UPDATE SET
                    ts = excluded.ts,
                    action = excluded.action,
                    cost = excluded.cost,
                    summary_json = excluded.summary_json
                """,
                (turn, utc_now_iso(), action, cost, json.dumps(summary, ensure_ascii=True)),
            )

    def append_events(self, turn: int, events: list[dict[str, object]]) -> None:
        if not events:
            return
        with self.conn:
            for event in events:
                self.conn.execute(
                    """
                    INSERT INTO events_log(turn, event_id, summary_json)
                    VALUES(?, ?, ?)
                    ON CONFLICT(turn, event_id) DO UPDATE SET
                        summary_json = excluded.summary_json
                    """,
                    (turn, str(event["id"]), json.dumps(event, ensure_ascii=True)),
                )

    def history(self, limit: int = 20) -> list[dict[str, object]]:
        rows = self.conn.execute(
            "SELECT * FROM history ORDER BY turn DESC LIMIT ?",
            (limit,),
        ).fetchall()
        result: list[dict[str, object]] = []
        for row in rows:
            result.append(
                {
                    "turn": int(row["turn"]),
                    "ts": row["ts"],
                    "action": row["action"],
                    "cost": int(row["cost"]),
                    "summary": json.loads(str(row["summary_json"])),
                }
            )
        return result

    def events_since(self, from_turn: int) -> list[dict[str, object]]:
        rows = self.conn.execute(
            "SELECT turn, event_id, summary_json FROM events_log WHERE turn >= ? ORDER BY turn DESC",
            (from_turn,),
        ).fetchall()
        out: list[dict[str, object]] = []
        for row in rows:
            event = json.loads(str(row["summary_json"]))
            event["turn"] = int(row["turn"])
            out.append(event)
        return out
