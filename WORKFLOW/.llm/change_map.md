# CHANGE_MAP (append-only)

Format:
MAP-XXXX | DATE | CHECKPOINT | CHG-ID | FILE | SYMBOL | ACTION | RATIONALE

Policy:
- enforce_from_chg: CHG-0019
- ACTION values: ADD | UPDATE | DELETE | MOVE | REFACTOR
- SYMBOL must be explicit (function/class/method/module section or FILE_SCOPE)

MAP-0001 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/.llm/LLM_RULES.md | Invariants/Drift guard sections | UPDATE | Added mandatory symbol-level change traceability rule and enforced CHG-to-MAP linkage
MAP-0002 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/.llm/PROTOCOL.md | Step sequence 9-14 | UPDATE | Inserted required change_map logging step after changes.md
MAP-0003 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/.llm/MANIFEST.md | Cold files list | UPDATE | Added change_map.md as cold tail-read governance file
MAP-0004 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/.llm/change_map.md | FILE_SCOPE | ADD | Added append-only symbol-level mapping contract and enforcement start marker
MAP-0005 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/check/audit_check.py | FILE_SCOPE | ADD | Added automatic policy checker with strict exit codes and report output
MAP-0006 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/check/README.md | Usage/Exit code sections | UPDATE | Documented audit command usage and validation coverage
MAP-0007 | 2026-02-18 | CP-0021 | CHG-0019 | PROJECT/requirements.txt | Dependency declaration section | UPDATE | Enforced locked constraints file in default install path
MAP-0008 | 2026-02-18 | CP-0021 | CHG-0019 | PROJECT/constraints.lock.txt | FILE_SCOPE | ADD | Pinned runtime/dev/UI dependencies including transitives for reproducible setups
MAP-0009 | 2026-02-18 | CP-0021 | CHG-0019 | setup.ps1 | dependency install block | UPDATE | Enforced lock-file usage in setup path and explicit lock-file existence guard
MAP-0010 | 2026-02-18 | CP-0021 | CHG-0019 | PROJECT/scripts/refresh_lock.ps1 | FILE_SCOPE | ADD | Added controlled lock regeneration workflow for intentional dependency updates
MAP-0011 | 2026-02-18 | CP-0021 | CHG-0019 | README.md | Workflow Traceability/Audit sections | UPDATE | Added user-facing documentation for symbol-level trace and audit execution
MAP-0012 | 2026-02-18 | CP-0021 | CHG-0019 | PROJECT/README.md | Audit/Lock sections | UPDATE | Added project-level instructions for lock refresh and audit checks
MAP-0013 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/README.md | Governance docs section | UPDATE | Added workflow traceability and automated check references
MAP-0014 | 2026-02-18 | CP-0021 | CHG-0019 | WORKFLOW/.llm/PROJECT_SUMMARY.md | Execution model chain | UPDATE | Extended chain with change_map stage between changes and implementation
MAP-0015 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/src/shinon_os/util/paths.py | default_docs_dir/default_transcript_dir | ADD | Added user-docs transcript paths under LOCALAPPDATA with auto-create behavior
MAP-0016 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/src/shinon_os/util/transcript.py | SessionTranscriptWriter | ADD | Added JSON+TXT session transcript writer with start/entry/finish/flush lifecycle
MAP-0017 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/src/shinon_os/app_service.py | transcript lifecycle methods + handle_input metadata | UPDATE | Wired transcript collection, idempotent finalize paths, and best-effort error handling
MAP-0018 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/src/shinon_os/app.py | run_app error/finalize control flow | UPDATE | Ensured transcripts finalize on successful exits and on uncaught base exceptions
MAP-0019 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/src/shinon_os/ui/plain_cli.py | PlainCliSession.run | UPDATE | Added explicit transcript finalize on quit and on runtime exception
MAP-0020 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/src/shinon_os/ui/textual_app.py | TextualSession._apply_response/run | UPDATE | Added transcript finalize hooks for should_quit and error path
MAP-0021 | 2026-02-18 | CP-0022 | CHG-0020 | WORKFLOW/check/audit_check.py | runtime independence validation | UPDATE | Added automated guard that PROJECT runtime code does not reference WORKFLOW/.llm
MAP-0022 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/tests/test_runtime_no_workflow_dependency.py | test_project_runtime_has_no_workflow_llm_dependency | ADD | Added static runtime isolation test against workflow governance coupling
MAP-0023 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/tests/test_fresh_system_state_persistence.py | test_fresh_system_persists_state_across_restarts | ADD | Added fresh-system persistence test using temporary LOCALAPPDATA state root
MAP-0024 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/tests/test_transcript_written_on_quit.py | test_transcript_written_on_quit | ADD | Added verification that quit emits transcript files and expected content
MAP-0025 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/tests/test_transcript_written_on_error.py | test_transcript_written_on_session_error | ADD | Added verification that session crash path writes error transcript
MAP-0026 | 2026-02-18 | CP-0022 | CHG-0020 | README.md | Session transcripts section | UPDATE | Documented transcript path, formats, and trigger semantics
MAP-0027 | 2026-02-18 | CP-0022 | CHG-0020 | PROJECT/README.md | Session transcripts section | UPDATE | Added project-level transcript behavior for operators
MAP-0028 | 2026-02-18 | CP-0022 | CHG-0020 | WORKFLOW/README.md | Session transcript runtime behavior section | UPDATE | Added workflow-side visibility for runtime transcript behavior
MAP-0029 | 2026-02-18 | CP-0022 | CHG-0020 | WORKFLOW/check/README.md | Validated areas section | UPDATE | Documented new checks for runtime isolation and transcript module presence
