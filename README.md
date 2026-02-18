# Shinon Alpha World

Repository layout:
- WORKFLOW/: universal workflow subsystem
- PROJECT/: project implementation
- WORKFLOW/check/temp/: temporary workflow check artifacts
- WORKFLOW/DOCS/: user-readable workflow result exports

See WORKFLOW/.llm/PROJECT_SUMMARY.md for system-level orientation.

Quick setup (from repo root):
- `.\setup.ps1`
- `.\start.ps1`
- `.\setup.ps1` creates a fresh isolated `.venv` by default on every run
- use `.\setup.ps1 -KeepVenv` to skip rebuild when needed

Double-click option:
- `setup.cmd` (one-time setup)
- `start.cmd` (start app)

Manual run (from `PROJECT/`):
- `python -m shinon_os` (Textual UI default)
- `python -m shinon_os --safe-ui` to force plain fallback
- `python -m shinon_os --no-anim` to disable boot/idle FX
- Runtime language command: `lang de` or `lang en`
- Gameplay helper commands: `unlock list`, `show goals`, `intel`

Workflow traceability:
- High-level file mapping: `WORKFLOW/.llm/changes.md`
- Symbol-level code mapping: `WORKFLOW/.llm/change_map.md`

Audit check:
- `python WORKFLOW/check/audit_check.py`
- Report output: `WORKFLOW/check/temp/audit_report.json`

Dependency lock refresh:
- `powershell -File PROJECT/scripts/refresh_lock.ps1`

Copilot transcripts:
- Separate from `PROJECT` runtime
- Tool: `WORKFLOW/tools/copilot_transcript.ps1`
- Saved to `%LOCALAPPDATA%/copilot_docs/transcripts`
- Written as `.json` and `.txt`

Workflow-Framework extrahieren:
- `python WORKFLOW/tools/extract_workflow_repo.py --target ../WorkflowKit-Framework --init-git`
- Export now includes locale files at `locales/de.json` and `locales/en.json`
- Standalone audit in extracted repo: `python check/audit_check.py --standalone`

Versioning automation:
- `.\version.ps1 -Bump patch`
- `.\version.ps1 -SetVersion 1.0.0`
- Script validates clean git status, syncs version in `PROJECT/pyproject.toml` + `PROJECT/src/shinon_os/__init__.py`, commits, and creates annotated tag `vX.Y.Z`.
- CMD wrapper: `version.cmd`

Backup automation:
- `.\backup.ps1`
- Creates ZIP backups in `BACKUPS/` with auto-increment naming: `Shinon mvp v_1.zip`, `Shinon mvp v_2.zip`, ...
- Backup is a clean snapshot (excludes `.git`, `.venv`, `PROJECT/.venv`, `BACKUPS`, `__pycache__`, `.pytest_cache`, `*.pyc`, `.vscode`).
- Writes latest backup path to `BACKUPS/latest_backup.txt`.
- CMD wrapper: `backup.cmd`
