# QUEUE

Format:
Q-XXXX | STATUS | TITLE | OWNER | REFERENCES

Status values:
- DRAFT
- READY
- IN_PROGRESS
- BLOCKED
- IMPLEMENTED

Rules:
- IMPLEMENTED entries must reference one or more Q-IDs.
- Queue IDs are monotonic and never reused.
- References can include I-ID, C-ID, D-ID, CHG-ID, and file paths.

Entries:
Q-0001 | IMPLEMENTED | Change map output and low-I/O workflow mode | codex | I-0002, C-0002, D-0002, CHG-0001
Q-0002 | IMPLEMENTED | SHINON-OS MVP bootstrap (workflow + code + tests + docs + data) | codex | I-0003, C-0003, D-0003, CHG-0002
Q-0003 | IMPLEMENTED | requirements.txt erstellen und befüllen | codex | I-0004, C-0004, D-0004, CHG-0003
Q-0004 | IMPLEMENTED | Rebranding auf Shinon Alpha World + Abhängigkeiten installiert + Tests bestätigt | codex | I-0005, C-0005, D-0005, CHG-0004

Next available ID: Q-0005
