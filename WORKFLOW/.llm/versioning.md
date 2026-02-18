# VERSIONING (append-only)

Format:
V-XXXX | DATE | CHECKPOINT | spec_rev | queue_rev | build_rev | NOTE

V-0001 | 2026-02-18 | CP-0002 | 2 | 1 | 0 | Workflowkit hardening baseline

V-0002 | 2026-02-18 | CP-0003 | 3 | 2 | 0 | Change map plus low-I/O mode
V-0003 | 2026-02-18 | CP-0004 | 5 | 4 | 1 | SHINON MVP build complete with deterministic kernel/sim/persistence/tests
V-0004 | 2026-02-18 | CP-0005 | 6 | 5 | 2 | requirements.txt added for dependency install
V-0005 | 2026-02-18 | CP-0006 | 7 | 6 | 3 | Rebrand to Shinon Alpha World, dependencies installed, tests green
V-0006 | 2026-02-18 | CP-0007 | 8 | 7 | 4 | Repository now contains full project tree (WORKFLOW + PROJECT), validated with pytest
V-0007 | 2026-02-18 | CP-0008 | 9 | 8 | 5 | Chat-first UI overhaul with fixed boot sequence, adapter architecture, and 11 passing tests
V-0008 | 2026-02-18 | CP-0009 | 10 | 9 | 5 | Rest tasks registered, Q-0007 opened, per-change logging baseline
V-0009 | 2026-02-18 | CP-0010 | 11 | 9 | 6 | AppService + ViewModels + UI flag wiring, core render decoupled
V-0010 | 2026-02-18 | CP-0011 | 12 | 9 | 7 | Textual frame rebuilt with hotkeys, canvas stub, service-driven views
V-0011 | 2026-02-18 | CP-0012 | 13 | 9 | 8 | Added UI mode and view model tests, animation flag coverage
V-0012 | 2026-02-18 | CP-0013 | 14 | 9 | 9 | Added help endpoint and README updates for UI flags and layout
V-0013 | 2026-02-18 | CP-0014 | 15 | 9 | 10 | Fallback hints for unknown commands, isolated DBs in UI tests, all tests passing (22)
V-0014 | 2026-02-18 | CP-0015 | 16 | 10 | 10 | Q-0007 implemented, OS-Illusion TUI MVP complete, queue closed
V-0015 | 2026-02-18 | CP-0016 | 17 | 11 | 10 | Structural correction finalized: WORKFLOW governance only, PROJECT code/data only, plus check/temp and user-readable DOCS outputs
V-0016 | 2026-02-18 | CP-0017 | 18 | 12 | 11 | requirements.txt now installs full setup via editable ui+dev extras; one-command complete environment
V-0017 | 2026-02-18 | CP-0018 | 19 | 13 | 12 | Textual compatibility fix landed for current release; startup no longer uses removed widget internals
V-0018 | 2026-02-18 | CP-0019 | 20 | 14 | 13 | Added one-step setup/start scripts and cmd wrappers for non-technical onboarding
V-0019 | 2026-02-18 | CP-0020 | 21 | 15 | 14 | Setup now recreates virtual environment by default to guarantee clean reproducible installs
