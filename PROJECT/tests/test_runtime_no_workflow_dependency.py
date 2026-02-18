from __future__ import annotations

import re
from pathlib import Path


def test_project_runtime_has_no_workflow_llm_dependency() -> None:
    src_root = Path(__file__).resolve().parents[1] / "src"
    pattern = re.compile(r"WORKFLOW[\\/]\.llm", flags=re.IGNORECASE)

    violations: list[str] = []
    for path in src_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            violations.append(str(path))

    assert not violations, "Runtime code references WORKFLOW/.llm:\n" + "\n".join(violations)
