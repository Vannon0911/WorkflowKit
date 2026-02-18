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
Q-0011 | IMPLEMENTED | Onboarding vereinfachen mit One-Step Setup/Start Skripten | codex | I-0011, C-0011, D-0012, CHG-0017
Q-0012 | IMPLEMENTED | Setup standardmäßig mit frischer venv erzwingen | codex | I-0012, C-0012, D-0013, CHG-0018
Q-0013 | IMPLEMENTED | Workflow-Trace-Regel auf Symbol-Ebene + automatischer Audit-Check + harte Dependency-Locks | codex | I-0013, C-0013, D-0014, CHG-0019
Q-0014 | IMPLEMENTED | Systemprüfung ohne .llm Runtime-Kopplung + automatische Session-Transkripte in User-DOCS | codex | I-0014, C-0014, D-0015, CHG-0020
Q-0015 | IMPLEMENTED | Copilot-Transkripte vom SHINON-Runtime-System trennen und als eigenes Workflow-Tool führen | codex | I-0015, C-0015, D-0016, CHG-0021
Q-0016 | IMPLEMENTED | Gesamt-MVP: DE/EN Locale-Runtime, Unlock/Collapse Gameplay, Standalone-Locale-Audit und Workflow-Hardening | codex | I-0016, C-0016, D-0017, CHG-0022
Q-0017 | IMPLEMENTED | .llm Sofort-Dokumentation als Agenten-Systemstandard | codex | I-0017, C-0017, D-0018, CHG-0023
Q-0018 | IMPLEMENTED | Umfassendes Projekt-Audit: 31/31 Tests, Gameplay-Substanz, Logik-Validierung und Bericht | codex | I-0017, C-0017, D-0018, CHG-0024

Next available ID: Q-0019
