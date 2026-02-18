# WORKFLOW Check

This folder contains workflow validation artifacts.

- `temp/` is reserved for temporary check outputs.
- Keep files disposable and non-essential.

## Automated audit check

Run:

```powershell
python WORKFLOW/check/audit_check.py
```

Exit codes:
- `0`: all checks passed
- `1`: policy/rule violations found
- `2`: format or parsing errors

Validated areas:
- mandatory `.llm` file presence
- CHG/MAP sequence integrity and references
- enforced CHG to MAP coverage
- state/current revision consistency
- queue IMPLEMENTED to CHG linkage
- dependency lock and setup lock enforcement
- runtime independence from `WORKFLOW/.llm` inside `PROJECT/src`
- copilot transcript tool presence (`WORKFLOW/tools/copilot_transcript.ps1`)

Report output:
- `WORKFLOW/check/temp/audit_report.json`
