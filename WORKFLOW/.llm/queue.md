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
Q-0005 | IMPLEMENTED | Repository soll das Projekt enthalten (PROJECT in Repo integriert und getestet) | codex | I-0006, C-0006, D-0006, CHG-0005
Q-0006 | IMPLEMENTED | UI Big-Bang: Bootscreen + Chat-first Flow + UI Adapter + neue Gates/Tests | codex | I-0007, C-0007, D-0007, CHG-0006
Q-0007 | IMPLEMENTED | OS-Illusion TUI Upgrade 100% MVP + WorkflowKit per-change logging | codex | D-0008, CHG-0008, CHG-0009, CHG-0010, CHG-0011, CHG-0012
Q-0008 | IMPLEMENTED | Strukturkorrektur: WORKFLOW rein fuer Workflow, PROJECT rein fuer Projektdaten + check/temp + DOCS | codex | I-0008, C-0008, D-0009, CHG-0014
Q-0009 | IMPLEMENTED | requirements.txt als Voll-Setup (alle Abhaengigkeiten) festlegen | codex | I-0009, C-0009, D-0010, CHG-0015
Q-0010 | IMPLEMENTED | Textual-UI Crash beheben und Terminal-Lesbarkeit verbessern | codex | I-0010, C-0010, D-0011, CHG-0016

Next available ID: Q-0011
