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
