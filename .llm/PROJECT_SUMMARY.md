# PROJECT_SUMMARY

Repository split:
- WORKFLOW/: universal governance, drift control, and state tracking.
- PROJECT/: real project code only.

Workflowkit goals:
- Prevent process drift.
- Enable complete and reproducible documentation.
- Preserve versioned intermediate steps (ideas, concepts, audits, trace).
- Keep storage LLM-friendly and machine-parseable.

Execution model:
- WORKFLOW/.llm is the only source of truth.
- state.json anchors checkpoint and revision counters.
- ideas.md -> concepts.md -> queue.md -> implementation forms the chain.
- trace.md and audit.md are append-only historical logs.
