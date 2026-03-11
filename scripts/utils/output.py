"""Output formatting utilities — JSON to stdout, status to stderr."""

from __future__ import annotations

import json
import sys
from typing import Any


def print_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def print_table(rows: list[dict[str, Any]], columns: list[str]) -> None:
    """Print rows as an aligned text table to stdout."""
    if not rows:
        print("(no results)")
        return

    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    header = "  ".join(col.upper().ljust(widths[col]) for col in columns)
    separator = "  ".join("-" * widths[col] for col in columns)
    print(header)
    print(separator)
    for row in rows:
        line = "  ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        print(line)


def print_success(message: str) -> None:
    """Print a success message to stderr."""
    print(f"ok: {message}", file=sys.stderr)


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"error: {message}", file=sys.stderr)
