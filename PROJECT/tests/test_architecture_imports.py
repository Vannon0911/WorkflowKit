from __future__ import annotations

from pathlib import Path


def _module_path_to_import(path: Path, src_root: Path) -> str:
    rel = path.relative_to(src_root).with_suffix("")
    return ".".join(rel.parts)


def test_architecture_imports_gate() -> None:
    src_root = Path(__file__).resolve().parents[1] / "src"
    forbidden_roots = ["shinon_os.ui", "shinon_os.ui."]
    guarded_dirs = [
        src_root / "shinon_os" / "core",
        src_root / "shinon_os" / "sim",
        src_root / "shinon_os" / "persistence",
    ]

    violations: list[str] = []
    for directory in guarded_dirs:
        for path in directory.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            mod_name = _module_path_to_import(path, src_root)
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("import shinon_os.ui") or stripped.startswith("from shinon_os.ui"):
                    violations.append(f"{mod_name}: {stripped}")
                if any(root in stripped for root in forbidden_roots) and ("import " in stripped):
                    violations.append(f"{mod_name}: {stripped}")
    assert not violations, "Forbidden ui imports detected:\n" + "\n".join(violations)
