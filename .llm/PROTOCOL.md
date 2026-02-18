# PROTOCOL

1. Read every file in WORKFLOW/.llm before any plan or change.
2. Validate mandatory file presence and revision consistency against state.json.
3. Log ideation in ideas.md (I-IDs, append-only chronology).
4. Log refined solution models in concepts.md (C-IDs, append-only chronology).
5. Register executable work in queue.md using Q-IDs and explicit status.
6. Record policy and architecture decisions in decisions.md (D-IDs).
7. Apply changes in PROJECT/ or WORKFLOW/ as required by the active Q-ID.
8. Update state.json revision counters and checkpoint when governance state changes.
9. Append trace.md and audit.md entries for each checkpoint-relevant transition.
10. Append versioning.md entry that snapshots checkpoint and revision counters.
11. Never store secrets.
