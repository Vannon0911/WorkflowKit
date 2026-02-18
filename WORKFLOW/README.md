# Shinon Alpha World

Repository layout:
- WORKFLOW/: universal workflow subsystem
- PROJECT/: project implementation
- WORKFLOW/check/temp/: temporary validation/check outputs
- WORKFLOW/DOCS/: user-readable documentation of workflow results

See WORKFLOW/.llm/PROJECT_SUMMARY.md for system-level orientation.

Governance traceability:
- `WORKFLOW/.llm/changes.md` for CHG to file-level mappings
- `WORKFLOW/.llm/change_map.md` for CHG to symbol-level mappings

Automated audit:
- `python WORKFLOW/check/audit_check.py`

Session transcript runtime behavior:
- `PROJECT` writes transcripts to `%LOCALAPPDATA%/shinon_os/docs/transcripts`
- output formats: `.json` and `.txt`
