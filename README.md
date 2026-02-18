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
