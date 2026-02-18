from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / "WORKFLOW"
PROJECT_LOCALES = ROOT / "PROJECT" / "src" / "shinon_os" / "data"


def read_checkpoint() -> str:
    current = (WORKFLOW_DIR / ".llm" / "CURRENT.md").read_text(encoding="utf-8")
    for line in current.splitlines():
        if line.lower().startswith("checkpoint:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def ensure_empty_target(target: Path, clobber: bool) -> None:
    if target.exists():
        if not clobber:
            sys.exit(f"Target exists: {target}. Use --clobber to overwrite.")
        shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)


def copy_tree(target: Path) -> None:
    items = [
        (WORKFLOW_DIR / ".llm", target / ".llm"),
        (WORKFLOW_DIR / "check", target / "check"),
        (WORKFLOW_DIR / "DOCS", target / "DOCS"),
        (WORKFLOW_DIR / "tools", target / "tools"),
        (WORKFLOW_DIR / "config.toml", target / "config.toml"),
        (WORKFLOW_DIR / "README.md", target / "README.md"),
    ]
    for src, dst in items:
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        else:
            if dst.exists():
                dst.unlink()
            shutil.copy2(src, dst)

    locales_target = target / "locales"
    locales_target.mkdir(parents=True, exist_ok=True)
    for locale_name in ("de.json", "en.json"):
        src = PROJECT_LOCALES / locale_name
        if not src.exists():
            sys.exit(f"Missing locale file for export: {src}")
        shutil.copy2(src, locales_target / locale_name)


def write_gitignore(target: Path) -> None:
    gitignore = target / ".gitignore"
    gitignore.write_text(
        "\n".join(
            [
                "__pycache__/",
                ".pytest_cache/",
                ".venv/",
                "check/temp/*.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def append_export_note(target: Path, checkpoint: str) -> None:
    stamp = datetime.utcnow().isoformat()
    note = (
        "\n---\n"
        f"Exported from WorkflowKit checkpoint {checkpoint} on {stamp} UTC.\n"
        "Source path: WORKFLOW/\n"
    )
    readme = target / "README.md"
    with readme.open("a", encoding="utf-8") as f:
        f.write(note)


def init_git(target: Path) -> None:
    subprocess.run(["git", "init"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "workflow-export"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "workflow-export@example.com"], cwd=target, check=True)
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "init: workflow framework"], cwd=target, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=target, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract WORKFLOW as standalone repository")
    parser.add_argument("--target", required=True, help="Destination directory for extracted repo")
    parser.add_argument("--clobber", action="store_true", help="Overwrite target if it exists")
    parser.add_argument("--init-git", action="store_true", help="Initialize git repository in target")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not WORKFLOW_DIR.exists():
        sys.exit("WORKFLOW directory not found. Run from repository root.")

    ensure_empty_target(target, clobber=args.clobber)
    copy_tree(target)
    write_gitignore(target)
    append_export_note(target, read_checkpoint())
    if args.init_git:
        init_git(target)
    print(f"Extracted WORKFLOW to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
