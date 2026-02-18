# PROTOCOL

1. Read MANIFEST.md and then read all hot files listed there.
2. Validate mandatory file presence and revision consistency against state.json.
3. Log ideation in ideas.md (I-IDs, append-only chronology).
4. Log refined solution models in concepts.md (C-IDs, append-only chronology).
5. Register executable work in queue.md using Q-IDs and explicit status.
6. Record policy and architecture decisions in decisions.md (D-IDs).
7. Apply changes in PROJECT/ or WORKFLOW/ as required by the active Q-ID.
8. Append one compact mapping row in changes.md: Q-ID -> files -> summary.
9. Append symbol-level mapping rows in change_map.md for each enforced code-relevant CHG-ID.
10. Update state.json revision counters and checkpoint when governance state changes.
11. Append trace.md and audit.md entries for each checkpoint-relevant transition.
12. Append versioning.md entry that snapshots checkpoint and revision counters.
13. Update CURRENT.md with latest IDs to avoid full-log scans.
14. Never store secrets.
