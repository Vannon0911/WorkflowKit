# PROJECT_SUMMARY

Repository split:
- WORKFLOW/: universal governance, drift control, and state tracking.
- PROJECT/: real project code only.
- Path rule: `WORKFLOW` and `PROJECT` are sibling folders at repository root level.

Workflowkit goals:
- Prevent process drift.
- Enable complete and reproducible documentation.
- Preserve versioned intermediate steps (ideas, concepts, changes, audits).
- Minimize I/O load with manifest + snapshot + tail-read strategy.

Execution model:
- WORKFLOW/.llm is the only source of truth.
- state.json anchors checkpoint and revision counters.
- ideas.md -> concepts.md -> queue.md -> changes.md -> change_map.md -> implementation forms the chain.
- trace.md and audit.md are append-only historical logs.
