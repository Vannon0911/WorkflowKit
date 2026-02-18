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

System defaults:
- doc_granularity = per_step
- doc_enforcement = agent_only
- reads_exempt = true
- retroactive_open_changes = true

Invariants:
- WORKFLOW/.llm is the only source of truth.
- state.json is authoritative for checkpoint and revision counters.
- trace.md is append-only.
- audit.md is append-only.
- IMPLEMENTED entries must reference Q-IDs.
- Every code-relevant CHG entry (from enforcement checkpoint onward) must have one or more MAP entries in change_map.md.
- Every mutating work step requires immediate .llm documentation in trace.md, changes.md, change_map.md (if enforced) and CURRENT.md.
- Read-only operations are exempt from immediate documentation.
- Retroactive documentation is required for currently open local changes.
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
- LLM must not execute a second mutating step before immediate documentation of the first mutating step is complete.