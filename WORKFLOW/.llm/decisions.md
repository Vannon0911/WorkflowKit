# DECISIONS

Format:
D-XXXX | DATE | CHECKPOINT | DECISION | RATIONALE

D-0001 | 2026-02-18 | CP-0002 | Workflowkit hardened with drift guard and complete step logging | Required for no-drift execution and LLM-safe documentation chain
D-0002 | 2026-02-18 | CP-0003 | Add compact change-mapping and low-I/O read strategy | Keep full traceability while reducing read/write overhead
D-0003 | 2026-02-18 | CP-0004 | Implement MVP with strict view/action turn semantics and deterministic RNG seeded by DB state | Meets gameplay invariants and reproducibility tests
D-0004 | 2026-02-18 | CP-0005 | Add PROJECT/requirements.txt with only required packages | Preserve minimal dependency surface and easy install path
D-0005 | 2026-02-18 | CP-0006 | Rename visible project identity to Shinon Alpha World and keep runtime package name unchanged | Avoid import/runtime regressions while applying requested rename
D-0006 | 2026-02-18 | CP-0007 | Keep existing WORKFLOW git repo and include project by adding WORKFLOW/PROJECT snapshot | Satisfies repo scope request without destructive git-root migration
D-0007 | 2026-02-18 | CP-0008 | Introduce chat-first UI orchestration with fixed boot sequence and strict architecture import gate | Enables major UX shift while preventing module coupling drift
D-0008 | 2026-02-18 | CP-0009 | Rest tasks registered for OS-Illusion TUI MVP with per-change WorkflowKit logging | Tasks: AppService façade, structured view models, UI flags, Textual frame, canvas/FX, placeholder UX safety, tests+docs, per-change governance logging
D-0009 | 2026-02-18 | CP-0016 | Enforce repository split: WORKFLOW only for governance artifacts, PROJECT only for project code/data; add WORKFLOW/check/temp and WORKFLOW/DOCS for visibility | Restores structural clarity while preserving executable project and human-readable workflow outputs
D-0010 | 2026-02-18 | CP-0017 | requirements.txt must always install full runtime/UI/dev stack through package extras | Aligns user expectation with one-command complete setup
D-0011 | 2026-02-18 | CP-0018 | Refactor Textual chat rendering to avoid removed `Static.renderable` API and use ASCII-safe UI labels/bars | Ensures startup stability on textual 8 and improves cross-terminal readability
D-0012 | 2026-02-18 | CP-0019 | Standardize onboarding via `setup.ps1`/`start.ps1` and `setup.cmd`/`start.cmd` at repo root | Makes setup approachable for users without Python/venv experience
D-0013 | 2026-02-18 | CP-0020 | Setup runs with a fresh virtual environment by default; `-KeepVenv` is explicit opt-out | Maximizes reproducibility and protects against polluted local Python state
D-0014 | 2026-02-18 | CP-0021 | Make symbol-level change maps mandatory from CHG-0019 onward and enforce via automated audit checker with strict exit codes | Closes audit gaps, catches bad implementations early, and ensures reproducible dependency installs via locked constraints
D-0015 | 2026-02-18 | CP-0022 | Persist transcripts in user docs path (`%LOCALAPPDATA%/shinon_os/docs/transcripts`) for quit and crash/error paths, and enforce no runtime `.llm` coupling in PROJECT code | Preserves traceability on fresh systems while keeping runtime independent from workflow governance files
D-0016 | 2026-02-18 | CP-0023 | Remove SHINON runtime transcript coupling and introduce standalone Copilot transcript script (`WORKFLOW/tools/copilot_transcript.ps1`) as transcript source of truth | Aligns transcript scope with user requirement and keeps SHINON focused on simulation runtime only
D-0017 | 2026-02-18 | CP-0024 | Default runtime language is `de` with `en` fallback; command interface remains stable (`lang`, `enact`, etc.), while unlock persistence and collapse-recovery gating are enforced in engine/repo | Delivers bilingual UX without parser fragmentation and keeps gameplay progression/recovery deterministic and testable
D-0018 | 2026-02-18 | CP-0025 | Every mutating step must be documented immediately in .llm logs (read-only steps exempt), including retroactive coverage for currently open local changes | Establishes system-standard trace discipline without introducing hard technical blockers in audit execution
D-0019 | 2026-02-18 | CP-0026 | Project audit confirms no critical bugs, balanced game mechanics, deterministic simulation and adequate player agency; defer enhancement/balancing work to post-MVP cycles | Validates MVP completeness and gates further scope creep—focus remains on stability over feature expansion
D-0020 | 2026-02-19 | CP-0027 | Implement debug mode with --debug flag for terminal input logging and add 20-test crash resilience suite before release | Ensures UI/UX stability is verified under edge cases and operator can diagnose runtime issues
