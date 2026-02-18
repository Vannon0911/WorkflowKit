# LLM_RULES

Source of truth:
- WORKFLOW/.llm

Mandatory files:
- state.json
- queue.md
- decisions.md
- ideas.md
- concepts.md
- versioning.md
- trace.md
- audit.md
- LLM_RULES.md
- PROTOCOL.md
- PROJECT_SUMMARY.md

Invariants:
- Read all files in WORKFLOW/.llm before planning or implementation.
- WORKFLOW/.llm is the only source of truth.
- state.json is authoritative for checkpoint and revision counters.
- trace.md is append-only.
- audit.md is append-only.
- IMPLEMENTED entries must reference Q-IDs.
- No secrets in any repository file.

Revision discipline:
- Increase spec_rev when governance/spec files change.
- Increase queue_rev when queue.md changes.
- Increase build_rev only when project code changes.

Drift guard:
- If any mandatory .llm file is missing: stop and report consistency break.
- If revisions do not match changed artifacts: stop and report drift.
- If checkpoint transition has no trace and audit record: stop and report drift.

LLM compliance:
- Every response must state whether the workflow is consistent.
- LLM must refuse to continue when LLM_RULES are violated.
