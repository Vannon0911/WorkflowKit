# SHINON // Alpha World

Deterministische Terminal-Wirtschaftssimulation mit einem regelbasierten SHINON-Kernel.

## Start

```bash
cd PROJECT
python -m shinon_os
```

## Tests

```bash
cd PROJECT
python -m pytest -q
```

## Hinweise

- Keine Netz-APIs, kein LLM, keine externen Laufzeitabhaengigkeiten.
- SQLite mit WAL, Foreign Keys und Migrationen.
- View-Kommandos treiben keine Zeit voran; Action-Kommandos treiben exakt einen Turn voran.
