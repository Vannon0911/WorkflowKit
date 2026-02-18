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

Cold files (tail-read by default):
- decisions.md
- ideas.md
- concepts.md
- changes.md
- versioning.md
- trace.md
- audit.md

Tail policy:
- Default tail depth: 50 entries per cold file.
- Full-file read only for audits, drift investigation, or explicit request.
