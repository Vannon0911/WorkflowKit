# SHINON // Alpha World

Deterministische Terminal-Wirtschaftssimulation mit einem regelbasierten SHINON-Kernel.

## Start

Einfachster Weg (vom Repo-Root aus):

```bash
./setup.ps1
./start.ps1
```

Hinweis: `setup.ps1` erstellt standardmäßig bei jedem Lauf eine frische `.venv` (isoliert, reproduzierbar).
Wenn du die vorhandene Umgebung behalten willst: `./setup.ps1 -KeepVenv`

Alternativ per Doppelklick:
- `setup.cmd`
- `start.cmd`

Manuell:

```bash
cd PROJECT
python -m pip install -r requirements.txt
python -m shinon_os
```

UI mode override and safety flags:

```bash
python -m shinon_os --ui plain        # force plain fallback
python -m shinon_os --ui textual      # prefer fullscreen Textual (default)
python -m shinon_os --safe-ui         # force safe/plain mode
python -m shinon_os --no-anim         # disable boot/idle/transition FX
```

## Tests

```bash
cd PROJECT
python -m pytest -q
```

## UI

- Default: fullscreen Textual frame (Header, World canvas, Delta/Events, Status, Chat, Input, Footer) with hotkeys 1..6, ?, Ctrl+Q, and `:` command palette.
- Fallback: plain mode routed through AppService (safe/no-anim friendly).
- Views do not advance turns; actions advance exactly one turn.

## Hinweise

- Keine Netz-APIs, kein LLM, keine externen Laufzeitabhaengigkeiten.
- SQLite mit WAL, Foreign Keys und Migrationen.
- View-Kommandos treiben keine Zeit voran; Action-Kommandos treiben exakt einen Turn voran.
- Start zeigt eine fixe OS-Bootsequenz und wechselt danach in einen chat-zentrierten Operator-Flow.
