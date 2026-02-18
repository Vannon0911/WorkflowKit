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
MAP-0030 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/src/shinon_os/app_service.py | transcript lifecycle methods + handle_input transcript entries | DELETE | Removed transcript ownership from SHINON runtime service
MAP-0031 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/src/shinon_os/app.py | run_app transcript finalize control flow | DELETE | Removed global transcript finalize hooks from runtime wrapper
MAP-0032 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/src/shinon_os/ui/plain_cli.py | PlainCliSession.run transcript finalize hooks | DELETE | Plain session no longer writes transcripts
MAP-0033 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/src/shinon_os/ui/textual_app.py | TextualSession transcript finalize hooks | DELETE | Textual session no longer writes transcripts
MAP-0034 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/src/shinon_os/util/transcript.py | SessionTranscriptWriter | DELETE | Removed SHINON-specific transcript implementation
MAP-0035 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/tests/test_transcript_written_on_quit.py | test_transcript_written_on_quit | DELETE | Removed tests tied to SHINON transcript behavior
MAP-0036 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/tests/test_transcript_written_on_error.py | test_transcript_written_on_session_error | DELETE | Removed tests tied to SHINON transcript behavior
MAP-0037 | 2026-02-18 | CP-0023 | CHG-0021 | WORKFLOW/tools/copilot_transcript.ps1 | FILE_SCOPE | ADD | Added standalone Copilot transcript lifecycle tool (start/add/finish)
MAP-0038 | 2026-02-18 | CP-0023 | CHG-0021 | WORKFLOW/check/audit_check.py | copilot transcript tool presence check | UPDATE | Audit now validates workflow transcript tool instead of SHINON module
MAP-0039 | 2026-02-18 | CP-0023 | CHG-0021 | README.md | Copilot transcripts section | UPDATE | Repointed transcript documentation to standalone workflow tool
MAP-0040 | 2026-02-18 | CP-0023 | CHG-0021 | PROJECT/README.md | Session transcript section | DELETE | Removed PROJECT runtime transcript documentation
MAP-0041 | 2026-02-18 | CP-0023 | CHG-0021 | WORKFLOW/README.md | Copilot transcript tooling section | UPDATE | Documented transcript ownership split and storage path
MAP-0042 | 2026-02-18 | CP-0023 | CHG-0021 | WORKFLOW/check/README.md | Validated areas section | UPDATE | Updated audit scope wording for copilot transcript tool
MAP-0043 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/i18n.py | set_lang/get_lang/t | ADD | Added runtime localization loader with EN fallback, cache and missing-key warning behavior
MAP-0044 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/de.json | FILE_SCOPE | ADD | Added German locale key-value catalog for UI/content and gameplay strings
MAP-0045 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/en.json | FILE_SCOPE | ADD | Added English locale key-value catalog and fallback source
MAP-0046 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/unlocks.json | FILE_SCOPE | ADD | Added unlock progression rules used by engine ramp/cooldown logic
MAP-0047 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/soft_goals.json | FILE_SCOPE | ADD | Added informational endless goal definitions with locale keys
MAP-0048 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/intel_hints.json | FILE_SCOPE | ADD | Added hint definitions for manual and rare auto-intel outputs
MAP-0049 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/persistence/schema.py | SCHEMA_VERSION/migrate_to_v3 | UPDATE | Introduced schema v3 with unlock table and language/collapse meta defaults plus strict-ramp migration
MAP-0050 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/persistence/repo.py | language/unlock/meta helpers | UPDATE | Added persistence APIs for locale, unlock state, collapse state and hint timing metadata
MAP-0051 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/sim/worldgen.py | DataBundle + new definitions | UPDATE | Extended bundle to load locale-key metadata, unlock rules, soft goals and intel hints
MAP-0052 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/sim/model.py | GameState.unlocked_policies | UPDATE | Added explicit unlocked-policy state to runtime model
MAP-0053 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/sim/engine.py | unlock/collapse/intel flow | UPDATE | Added unlock ramp+cooldown, collapse recovery gating, emergency policy visibility, goals/intel helpers and cashflow summaries
MAP-0054 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/sim/events.py | apply_event return payload | UPDATE | Event output now resolves locale keys for label/description
MAP-0055 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/blocks/interpret.py | command parsing + policy hints | UPDATE | Added `lang`, `unlock list`, `show goals`, `intel` command intents and expanded policy hint mappings
MAP-0056 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/kernel.py | intent handlers + localized rendering | UPDATE | Added locale-switch handling, unlock/goals/intel commands, auto-hint injection and localized view/action output
MAP-0057 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/blocks/plan.py | heuristic map + locale notes | UPDATE | Added new policy heuristics and localized predictive note/status text
MAP-0058 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/blocks/narrate.py | render_action_report/render_view_header | UPDATE | Localized report/header labels while preserving deterministic action summary structure
MAP-0059 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/phrasebank.py | phrase key model | UPDATE | Switched phrase selection to locale keys for DE/EN rendering
MAP-0060 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/app_service.py | menu/help/response locale wiring | UPDATE | Added localized menu/help text, locale-changed propagation and new command discoverability
MAP-0061 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/app.py | app init locale sync | UPDATE | Runtime now initializes active locale from persisted language metadata
MAP-0062 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/ui/plain_cli.py | startup/prompt text | UPDATE | Plain UI prompts now resolve from locale keys
MAP-0063 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/ui/textual_app.py | labels/help/locale refresh | UPDATE | Textual UI now localizes labels and refreshes visible text after runtime language change
MAP-0064 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/view_models.py | OSResponse.locale_changed | UPDATE | Added locale_changed contract for UI refresh signaling
MAP-0065 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/intents.py | LANG/UNLOCK_LIST/SHOW_GOALS/INTEL constants | UPDATE | Extended intent surface for new operator commands
MAP-0066 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/core/types.py | KernelResponse.locale_changed | UPDATE | Added response flag to propagate runtime language switch events
MAP-0067 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/policies.json | locale keys + new tiers/emergency policies | UPDATE | Added key-based labels/descriptions, tier-2/3 policies and collapse-only emergency policies
MAP-0068 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/src/shinon_os/data/events.json | locale keys + systemic event expansion | UPDATE | Added locale-keyed labels/descriptions and extra systemic counter-force events
MAP-0069 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/tests/test_i18n_locale.py | FILE_SCOPE | ADD | Added coverage for locale fallback, missing-key marker and language persistence command
MAP-0070 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/tests/test_unlocks_and_collapse.py | FILE_SCOPE | ADD | Added unlock ramp/cooldown and collapse recovery/emergency policy lifecycle tests
MAP-0071 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/tests/test_migrations.py | schema version expectations | UPDATE | Updated migration assertions for schema v3 and unlock/language metadata
MAP-0072 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/tests/test_actions_advance_once.py | default action policy | UPDATE | Updated action-advance baseline to start-loadout policy under new unlock constraints
MAP-0073 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/tests/test_chat_intent_auto_execute.py | expected executed_action | UPDATE | Updated auto-execute expectation to unlocked policy for deterministic startup behavior
MAP-0074 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/tests/test_command_compatibility.py | action compatibility scenario | UPDATE | Adjusted compatibility action path to unlocked command under gated progression
MAP-0075 | 2026-02-18 | CP-0024 | CHG-0022 | WORKFLOW/check/audit_check.py | locale-file validation | UPDATE | Audit now enforces locale file presence in monorepo and standalone layouts
MAP-0076 | 2026-02-18 | CP-0024 | CHG-0022 | WORKFLOW/tools/extract_workflow_repo.py | locale copy stage | UPDATE | Standalone export now includes DE/EN locale artifacts in `locales/` for standalone audit compatibility
MAP-0077 | 2026-02-18 | CP-0024 | CHG-0022 | README.md | language/export/audit usage sections | UPDATE | Documented runtime language switching and locale-aware standalone workflow verification
MAP-0078 | 2026-02-18 | CP-0024 | CHG-0022 | PROJECT/README.md | UI command notes section | UPDATE | Added language-select and unlock/goals/intel command guidance for operators
MAP-0079 | 2026-02-18 | CP-0024 | CHG-0022 | WORKFLOW/README.md | standalone locale requirement note | UPDATE | Added explicit locale artifact requirement for standalone audit mode
MAP-0080 | 2026-02-18 | CP-0024 | CHG-0022 | WORKFLOW/check/README.md | validated areas list | UPDATE | Added locale validation coverage details for monorepo and standalone modes
MAP-0081 | 2026-02-18 | CP-0025 | CHG-0023 | WORKFLOW/.llm/PROTOCOL.md | mutating-step sequence rules | UPDATE | Added immediate per-step documentation order and prohibition on starting next mutation early
MAP-0082 | 2026-02-18 | CP-0025 | CHG-0023 | WORKFLOW/.llm/LLM_RULES.md | System defaults + Invariants + LLM compliance | UPDATE | Formalized agent-only immediate documentation policy with read-only exemption and retroactive-open-change requirement
MAP-0083 | 2026-02-18 | CP-0025 | CHG-0023 | WORKFLOW/.llm/MANIFEST.md | Mutation-active governance files section | UPDATE | Declared trace/changes/change_map/current as mandatory live files during mutating work
MAP-0084 | 2026-02-18 | CP-0025 | CHG-0023 | WORKFLOW/.llm/state.json | checkpoint/revision fields + doc policy keys | UPDATE | Advanced CP/spec/queue/step and persisted immediate-doc mode metadata
MAP-0085 | 2026-02-18 | CP-0025 | CHG-0023 | WORKFLOW/.llm/CURRENT.md | checkpoint/revision snapshot + latest IDs | UPDATE | Synced current governance snapshot with CP-0025 and latest I/C/D/Q/CHG/MAP/V/T/A pointers
MAP-0086 | 2026-02-18 | CP-0025 | CHG-0023 | version.ps1 | FILE_SCOPE | ADD | Retroactively documented version automation flow (semver sync, clean-tree guard, commit+tag policy)
MAP-0087 | 2026-02-18 | CP-0025 | CHG-0023 | version.cmd | FILE_SCOPE | ADD | Retroactively documented cmd wrapper entrypoint for version.ps1
MAP-0088 | 2026-02-18 | CP-0025 | CHG-0023 | backup.ps1 | FILE_SCOPE | ADD | Retroactively documented clean snapshot backup flow with exclusions and auto-increment naming
MAP-0089 | 2026-02-18 | CP-0025 | CHG-0023 | backup.cmd | FILE_SCOPE | ADD | Retroactively documented cmd wrapper entrypoint for backup.ps1
MAP-0090 | 2026-02-18 | CP-0025 | CHG-0023 | README.md | Versioning automation + Backup automation sections | UPDATE | Retroactively mapped user-facing documentation for new version/backup scripts and usage rules
MAP-0091 | 2026-02-18 | CP-0026 | CHG-0024 | PROJECT_AUDIT_REPORT.md | FILE_SCOPE | ADD | Added comprehensive system audit report covering governance, subsystem validation, edge case testing, balance analysis and recommendations
MAP-0092 | 2026-02-18 | CP-0026 | CHG-0024 | WORKFLOW/.llm/audit.md | verification results | UPDATE | Recorded audit completion with all tests passed and design validation confirmed
