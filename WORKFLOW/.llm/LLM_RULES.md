# LLM_RULES

Source of truth:
- WORKFLOW/.llm

Mandatory files:
- state.json
- MANIFEST.md
- CURRENT.md
- queue.md
- decisions.md
- ideas.md
- concepts.md
- changes.md
- change_map.md
- versioning.md
- trace.md
- audit.md
- LLM_RULES.md
- PROTOCOL.md
- PROJECT_SUMMARY.md
- PROJECT/src/shinon_os/data/de.json
- PROJECT/src/shinon_os/data/en.json

Invariants:
- WORKFLOW/.llm is the only source of truth.
- state.json is authoritative for checkpoint and revision counters.
- trace.md is append-only.
- audit.md is append-only.
- IMPLEMENTED entries must reference Q-IDs.
- Every code-relevant CHG entry (from enforcement checkpoint onward) must have one or more MAP entries in change_map.md.
- No secrets in any repository file.

Revision discipline:
- Increase spec_rev when governance/spec files change.
- Increase queue_rev when queue.md changes.
- Increase build_rev only when project code changes.

Drift guard:
- If any mandatory .llm file is missing: stop and report consistency break.
- If mandatory locale artifacts are missing: stop and report consistency break.
- If revisions do not match changed artifacts: stop and report drift.
- If checkpoint transition has no trace and audit record: stop and report drift.
- Every IMPLEMENTED Q-ID must have a matching changes.md entry.
- Every enforced CHG-ID must have at least one valid MAP entry with FILE/SYMBOL/ACTION/RATIONALE.

I/O policy:
- Read MANIFEST.md first.
- Read all hot files listed in MANIFEST.md.
- Read cold logs in tail mode using CURRENT.md pointers unless full audit is requested.
- Keep high-frequency entries compact and one-line parseable.

LLM compliance:
- Every response must state whether the workflow is consistent.
- LLM must refuse to continue when LLM_RULES are violated.
