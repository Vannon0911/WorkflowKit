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
