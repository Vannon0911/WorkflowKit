# CONCEPTS (append-only)

Format:
C-XXXX | DATE | CHECKPOINT | CONCEPT | REFERENCES

C-0001 | 2026-02-18 | CP-0002 | Three-phase governance chain (idea -> concept -> queue) with auditable checkpointing | I-0001, D-0001

C-0002 | 2026-02-18 | CP-0003 | Manifest/snapshot/tail model with changes.md mapping | I-0002, D-0002
C-0003 | 2026-02-18 | CP-0004 | Deterministic SHINON kernel pipeline (sense->interpret->stance->plan->execute->narrate) over SQLite-backed economy sim | I-0003
C-0004 | 2026-02-18 | CP-0005 | Keep requirements minimal: stdlib runtime + pytest for tests in requirements.txt | I-0004
C-0005 | 2026-02-18 | CP-0006 | Rebrand via metadata/docs only (README + pyproject + state project id) without module-path breakage | I-0005
C-0006 | 2026-02-18 | CP-0007 | Sync root PROJECT into repository-local WORKFLOW/PROJECT and validate there with pytest | I-0006
C-0007 | 2026-02-18 | CP-0008 | Dual-mode UI architecture (Textual primary, plain fallback) with boot model and chat-turn model contracts | I-0007
C-0008 | 2026-02-18 | CP-0016 | Keep one canonical PROJECT at repository root, keep WORKFLOW purely governance, and expose workflow result summaries in WORKFLOW/DOCS | I-0008
C-0009 | 2026-02-18 | CP-0017 | Define requirements.txt as a full-environment installer via editable extras (ui+dev) instead of partial package list | I-0009
C-0010 | 2026-02-18 | CP-0018 | Keep chat log state in app-owned buffer instead of widget internals to stay compatible across Textual releases | I-0010
C-0011 | 2026-02-18 | CP-0019 | Provide root-level setup/start scripts with cmd wrappers and sensible defaults | I-0011
C-0012 | 2026-02-18 | CP-0020 | Default to rebuilding `.venv` in setup script, with explicit opt-out switch for fast reuse | I-0012
C-0013 | 2026-02-18 | CP-0021 | Introduce enforced CHG->MAP symbol mapping with automated validation and locked dependency graph checks | I-0013
C-0014 | 2026-02-18 | CP-0022 | Session transcript writer in LOCALAPPDATA docs with JSON+TXT dual output and best-effort crash finalization | I-0014
C-0015 | 2026-02-18 | CP-0023 | Transcript ownership split: SHINON keeps gameplay runtime only, Copilot transcripts handled by dedicated workflow tool with append lifecycle | I-0015
C-0016 | 2026-02-18 | CP-0024 | Introduce locale-keyed content model (with fallback labels), persisted unlock state, and collapse-gated emergency policy surface while keeping command syntax stable | I-0016
C-0017 | 2026-02-18 | CP-0025 | Step-atomic governance flow: every mutation is immediately mirrored into trace/changes/change_map/current before the next mutation | I-0017
C-0018 | 2026-02-18 | CP-0026 | Project audit validates zero critical bugs, complete game mechanics, deterministic reproducibility, and player agency balance across 31-test suite | I-0017, D-0019
C-0019 | 2026-02-19 | CP-0027 | Debug mode with terminal I/O logging and 20-crash test suite ensures UI stability against invalid/edge-case inputs before public release | I-0018, D-0020
