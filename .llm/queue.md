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
- References can include I-ID, C-ID, D-ID, and file paths.

Open items:
- none

Next available ID: Q-0001
