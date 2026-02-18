# DECISIONS

Format:
D-XXXX | DATE | CHECKPOINT | DECISION | RATIONALE

D-0001 | 2026-02-18 | CP-0002 | Workflowkit hardened with drift guard and complete step logging | Required for no-drift execution and LLM-safe documentation chain
D-0002 | 2026-02-18 | CP-0003 | Add compact change-mapping and low-I/O read strategy | Keep full traceability while reducing read/write overhead
D-0003 | 2026-02-18 | CP-0004 | Implement MVP with strict view/action turn semantics and deterministic RNG seeded by DB state | Meets gameplay invariants and reproducibility tests
D-0004 | 2026-02-18 | CP-0005 | Add PROJECT/requirements.txt with only required packages | Preserve minimal dependency surface and easy install path
D-0005 | 2026-02-18 | CP-0006 | Rename visible project identity to Shinon Alpha World and keep runtime package name unchanged | Avoid import/runtime regressions while applying requested rename
