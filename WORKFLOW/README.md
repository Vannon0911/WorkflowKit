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

Copilot transcript tooling (separate from PROJECT runtime):
- Script: `WORKFLOW/tools/copilot_transcript.ps1`
- Storage path: `%LOCALAPPDATA%/copilot_docs/transcripts`
- Formats: `.json` and `.txt`

Standalone nutzen (ohne PROJECT):
- `python check/audit_check.py --standalone`
- Optional: `python tools/extract_workflow_repo.py --target ../WorkflowKit-Framework --init-git`
