from __future__ import annotations

from typing import Iterable


def render_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    rows_list = [headers, *rows]
    widths = [max(len(str(row[idx])) for row in rows_list) for idx in range(len(headers))]
    line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    sep = "-+-".join("-" * w for w in widths)
    body = [" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)) for row in rows]
    return "\n".join([line, sep, *body])
