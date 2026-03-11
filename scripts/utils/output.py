"""Output formatting utilities — JSON to stdout, rich status to stderr."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.text import Text

from .style import (
    ICON_ERROR,
    ICON_INFO,
    ICON_SUCCESS,
    ICON_WARNING,
    status_style,
)


def status_console() -> Console:
    """Create a Console for stderr (rich formatting when TTY).

    A fresh Console is created each call so it always references the
    current ``sys.stderr`` — important when pytest's capsys swaps it.

    This function is part of the internal API shared across the utils
    package (used by both output.py and errors.py).
    """
    return Console(file=sys.stderr, highlight=False)


# ---------------------------------------------------------------------------
# stdout functions — plain text, no color, no Rich (machine-consumable)
# ---------------------------------------------------------------------------


def print_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def print_table(rows: list[dict[str, Any]], columns: list[str]) -> None:
    """Print rows as an aligned text table to stdout.

    Column names are uppercased in the header automatically.
    """
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


# ---------------------------------------------------------------------------
# stderr functions — rich formatting with icons and color
# ---------------------------------------------------------------------------


def _print_styled(icon: str, prefix: str, style: str, message: str) -> None:
    """Print a styled status message to stderr (icon + prefix + message)."""
    text = Text()
    text.append(f"{icon} ", style=style)
    text.append(f"{prefix}: ", style=f"{style} bold")
    text.append(message)
    status_console().print(text)


def print_success(message: str) -> None:
    """Print a success message to stderr with green checkmark."""
    _print_styled(ICON_SUCCESS, "ok", "green", message)


def print_error(message: str) -> None:
    """Print an error message to stderr with red x-mark."""
    _print_styled(ICON_ERROR, "error", "red", message)


def print_warning(message: str) -> None:
    """Print a warning message to stderr with yellow warning icon."""
    _print_styled(ICON_WARNING, "warning", "yellow", message)


def print_info(message: str) -> None:
    """Print an info message to stderr with blue info icon."""
    text = Text()
    text.append(f"{ICON_INFO} ", style="blue")
    text.append(message)
    status_console().print(text)


def print_status(label: str, value: str) -> None:
    """Print a label: value pair to stderr, with value colored by status."""
    text = Text()
    text.append(f"{label}: ", style="bold")
    text.append(value, style=status_style(value))
    status_console().print(text)


def print_diff_stat(additions: int, deletions: int) -> None:
    """Print diff stats like '+42 -17' with green/red coloring to stderr."""
    text = Text()
    text.append(f"+{additions}", style="green")
    text.append(" ")
    text.append(f"-{deletions}", style="red")
    status_console().print(text)


def print_section(title: str) -> None:
    """Print a section header (bold) to stderr."""
    status_console().print(Text(title, style="bold"))


def print_items(items: list[str], *, bullet: str = "-") -> None:
    """Print a bulleted list to stderr."""
    console = status_console()
    for item in items:
        console.print(f"  {bullet} {item}")
