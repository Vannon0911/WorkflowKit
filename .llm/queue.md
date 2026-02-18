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

Next available ID: Q-0002
