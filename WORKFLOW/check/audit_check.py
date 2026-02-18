from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


class ParseError(Exception):
    pass


@dataclass
class ChangeRow:
    chg_num: int
    chg_id: str
    scope: str
    files: list[str]


@dataclass
class MapRow:
    map_num: int
    chg_id: str
    file: str
    symbol: str
    action: str
    rationale: str


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / "WORKFLOW"
LLM_DIR = WORKFLOW_DIR / ".llm"
PROJECT_DIR = ROOT / "PROJECT"
TEMP_DIR = WORKFLOW_DIR / "check" / "temp"
REPORT_PATH = TEMP_DIR / "audit_report.json"

ALLOWED_ACTIONS = {"ADD", "UPDATE", "DELETE", "MOVE", "REFACTOR"}
MANDATORY_FILES = [
    "state.json",
    "MANIFEST.md",
    "CURRENT.md",
    "queue.md",
    "decisions.md",
    "ideas.md",
    "concepts.md",
    "changes.md",
    "change_map.md",
    "versioning.md",
    "trace.md",
    "audit.md",
    "LLM_RULES.md",
    "PROTOCOL.md",
    "PROJECT_SUMMARY.md",
]


def read_text(path: Path) -> str:
    if not path.exists():
        raise ParseError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def parse_changes(path: Path) -> list[ChangeRow]:
    rows: list[ChangeRow] = []
    text = read_text(path)
    for line in text.splitlines():
        if not re.match(r"^CHG-\d{4}\b", line):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            raise ParseError(f"Malformed CHG row: {line}")
        chg_id = parts[0]
        chg_num = int(chg_id.split("-")[1])
        scope = parts[4]
        files = [f.strip() for f in parts[5].split(";") if f.strip()]
        rows.append(ChangeRow(chg_num=chg_num, chg_id=chg_id, scope=scope, files=files))
    if not rows:
        raise ParseError("No CHG rows found")
    return rows


def parse_enforce_from_chg(text: str) -> int:
    match = re.search(r"enforce_from_chg:\s*CHG-(\d{4})", text)
    if not match:
        raise ParseError("change_map policy must define enforce_from_chg")
    return int(match.group(1))


def parse_change_map(path: Path) -> tuple[int, list[MapRow]]:
    rows: list[MapRow] = []
    text = read_text(path)
    enforce_from_chg = parse_enforce_from_chg(text)
    for line in text.splitlines():
        if not re.match(r"^MAP-\d{4}\b", line):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 8:
            raise ParseError(f"Malformed MAP row: {line}")
        map_id = parts[0]
        chg_id = parts[3]
        file = parts[4]
        symbol = parts[5]
        action = parts[6]
        rationale = parts[7]
        if action not in ALLOWED_ACTIONS:
            raise ParseError(f"Invalid ACTION '{action}' in row: {line}")
        if not symbol:
            raise ParseError(f"Empty SYMBOL in row: {line}")
        if not rationale:
            raise ParseError(f"Empty RATIONALE in row: {line}")
        rows.append(
            MapRow(
                map_num=int(map_id.split("-")[1]),
                chg_id=chg_id,
                file=file,
                symbol=symbol,
                action=action,
                rationale=rationale,
            )
        )
    if not rows:
        raise ParseError("No MAP rows found")
    return enforce_from_chg, rows


def parse_current(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    text = read_text(path)
    for key in ("checkpoint", "spec_rev", "queue_rev", "build_rev"):
        match = re.search(rf"^{key}:\s*(.+)$", text, flags=re.MULTILINE)
        if not match:
            raise ParseError(f"CURRENT.md missing key: {key}")
        result[key] = match.group(1).strip()
    return result


def parse_queue_implemented_refs(path: Path) -> list[str]:
    refs: list[str] = []
    for line in read_text(path).splitlines():
        if not re.match(r"^Q-\d{4}\b", line):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            raise ParseError(f"Malformed Q row: {line}")
        status = parts[1]
        ref = parts[4]
        if status == "IMPLEMENTED":
            refs.append(ref)
    return refs


def parse_constraints(path: Path) -> set[str]:
    text = read_text(path)
    pinned: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not re.match(r"^[A-Za-z0-9_.-]+==[^=]+$", stripped):
            raise ParseError(f"Invalid lock line: {stripped}")
        pinned.add(stripped.split("==")[0].lower())
    return pinned


def check_sequence(nums: list[int], label: str, errors: list[str]) -> None:
    if len(set(nums)) != len(nums):
        errors.append(f"{label} contains duplicate IDs")
        return
    ordered = sorted(nums)
    expected = list(range(ordered[0], ordered[-1] + 1))
    if ordered != expected:
        missing = sorted(set(expected) - set(ordered))
        errors.append(f"{label} sequence has gaps: {missing}")


def main() -> int:
    errors: list[str] = []
    parse_errors: list[str] = []

    try:
        missing = [f for f in MANDATORY_FILES if not (LLM_DIR / f).exists()]
        if missing:
            errors.append(f"Missing mandatory .llm files: {', '.join(missing)}")

        changes = parse_changes(LLM_DIR / "changes.md")
        enforce_from_chg, map_rows = parse_change_map(LLM_DIR / "change_map.md")
        current = parse_current(LLM_DIR / "CURRENT.md")
        state = json.loads(read_text(LLM_DIR / "state.json"))

        check_sequence([r.chg_num for r in changes], "CHG", errors)
        check_sequence([r.map_num for r in map_rows], "MAP", errors)

        chg_ids = {r.chg_id for r in changes}
        deleted_files_by_map: dict[str, list[int]] = {}
        for row in map_rows:
            if row.action == "DELETE":
                deleted_files_by_map.setdefault(row.file, []).append(row.map_num)

        map_by_chg: dict[str, list[MapRow]] = {}
        for row in map_rows:
            if row.chg_id not in chg_ids:
                errors.append(f"MAP references unknown CHG: {row.chg_id}")
            map_by_chg.setdefault(row.chg_id, []).append(row)
            if row.action != "DELETE":
                target = ROOT / row.file
                if not target.exists():
                    deleted_later = any(n > row.map_num for n in deleted_files_by_map.get(row.file, []))
                    if not deleted_later:
                        errors.append(f"MAP file does not exist: {row.file}")

        for change in changes:
            if change.chg_num < enforce_from_chg:
                continue
            if change.chg_id not in map_by_chg:
                errors.append(f"Missing MAP for enforced CHG: {change.chg_id}")

        if str(state.get("checkpoint")) != current["checkpoint"]:
            errors.append("state.json checkpoint mismatch CURRENT.md")
        for key in ("spec_rev", "queue_rev", "build_rev"):
            if str(state.get(key)) != current[key]:
                errors.append(f"state.json {key} mismatch CURRENT.md")

        queue_refs = parse_queue_implemented_refs(LLM_DIR / "queue.md")
        for ref in queue_refs:
            q_chg_ids = re.findall(r"CHG-\d{4}", ref)
            if not q_chg_ids:
                errors.append(f"IMPLEMENTED queue row missing CHG reference: {ref}")
            for q_chg in q_chg_ids:
                if q_chg not in chg_ids:
                    errors.append(f"Queue references unknown CHG: {q_chg}")

        requirements_text = read_text(PROJECT_DIR / "requirements.txt")
        if "-c constraints.lock.txt" not in requirements_text:
            errors.append("requirements.txt must include '-c constraints.lock.txt'")

        lock_packages = parse_constraints(PROJECT_DIR / "constraints.lock.txt")
        for required_pkg in ("pytest", "textual", "rich"):
            if required_pkg not in lock_packages:
                errors.append(f"constraints.lock.txt missing required package: {required_pkg}")

        setup_text = read_text(ROOT / "setup.ps1")
        if "constraints.lock.txt" not in setup_text:
            errors.append("setup.ps1 must enforce dependency lock file")

        copilot_transcript_tool = WORKFLOW_DIR / "tools" / "copilot_transcript.ps1"
        if not copilot_transcript_tool.exists():
            errors.append("Missing copilot transcript tool: WORKFLOW/tools/copilot_transcript.ps1")

        workflow_ref_pattern = re.compile(r"WORKFLOW[\\/]\.llm", flags=re.IGNORECASE)
        for py_file in (PROJECT_DIR / "src").rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            if workflow_ref_pattern.search(text):
                rel = py_file.relative_to(ROOT)
                errors.append(f"Runtime code must not reference WORKFLOW/.llm: {rel}")

    except ParseError as exc:
        parse_errors.append(str(exc))
    except Exception as exc:  # pragma: no cover
        parse_errors.append(f"Unhandled parse/runtime error: {exc}")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "ok": not errors and not parse_errors,
        "parse_errors": parse_errors,
        "errors": errors,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if parse_errors:
        for item in parse_errors:
            print(f"PARSE_ERROR: {item}")
        return 2
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1
    print("AUDIT_CHECK: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
