# MANIFEST

Read order:
1. state.json
2. LLM_RULES.md
3. PROTOCOL.md
4. CURRENT.md
5. queue.md

Hot files (always read):
- state.json
- LLM_RULES.md
- PROTOCOL.md
- CURRENT.md
- queue.md

Mutation-active governance files (must be updated immediately for mutating steps):
- trace.md
- changes.md
- change_map.md
- CURRENT.md

Cold files (tail-read by default):
- decisions.md
- ideas.md
- concepts.md
- changes.md
- change_map.md
- versioning.md
- trace.md
- audit.md
- PROJECT/src/shinon_os/data/de.json
- PROJECT/src/shinon_os/data/en.json

Tail policy:
- Default tail depth: 50 entries per cold file.
- Full-file read only for audits, drift investigation, or explicit request.