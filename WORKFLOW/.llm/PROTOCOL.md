# PROTOCOL

1. Read MANIFEST.md and then read all hot files listed there.
2. Validate mandatory file presence and revision consistency against state.json.
3. Log ideation in ideas.md (I-IDs, append-only chronology).
4. Log refined solution models in concepts.md (C-IDs, append-only chronology).
5. Register executable work in queue.md using Q-IDs and explicit status.
6. Record policy and architecture decisions in decisions.md (D-IDs).
7. Apply one mutating work step in PROJECT/ or WORKFLOW/ as required by the active Q-ID.
8. Immediately append trace.md entry (T-ID) for that step before any next mutation.
9. Immediately append one compact row in changes.md (CHG-ID) for that step.
10. For enforced code-relevant CHG-IDs, immediately append symbol-level map rows in change_map.md (MAP-IDs).
11. Immediately update CURRENT.md latest IDs after step documentation.
12. Never start another mutating step until steps 8-11 are complete.
13. Update state.json revision counters and checkpoint when governance state changes.
14. Append audit.md and versioning.md entries for each checkpoint-relevant transition.
15. Never store secrets.