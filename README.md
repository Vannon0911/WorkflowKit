# Shinon Alpha World

Repository layout:
- WORKFLOW/: universal workflow subsystem
- PROJECT/: project implementation
- WORKFLOW/check/temp/: temporary workflow check artifacts
- WORKFLOW/DOCS/: user-readable workflow result exports

See WORKFLOW/.llm/PROJECT_SUMMARY.md for system-level orientation.

Run (from PROJECT/):
- `python -m shinon_os` (Textual UI default)
- `python -m shinon_os --safe-ui` to force plain fallback
- `python -m shinon_os --no-anim` to disable boot/idle FX
