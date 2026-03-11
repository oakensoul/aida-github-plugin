"""Style constants for rich terminal output — icons, colors, status mappings."""

from __future__ import annotations

from typing import NamedTuple

# ---------------------------------------------------------------------------
# Icons — Unicode symbols, always paired with text for accessibility
# ---------------------------------------------------------------------------
ICON_SUCCESS = "\u2714"  # ✔
ICON_ERROR = "\u2718"  # ✘
ICON_WARNING = "\u26a0"  # ⚠
ICON_INFO = "\u2139"  # ℹ
ICON_PENDING = "\u25cb"  # ○


class _StatusEntry(NamedTuple):
    style: str
    icon: str


# ---------------------------------------------------------------------------
# Single source of truth: status → (rich style, icon)
# Keys are lowercase — lookup functions normalize input via .lower()
# ---------------------------------------------------------------------------
_STATUS_MAP: dict[str, _StatusEntry] = {
    # Success / positive
    "success": _StatusEntry("green", ICON_SUCCESS),
    "completed": _StatusEntry("green", ICON_SUCCESS),
    "merged": _StatusEntry("green", ICON_SUCCESS),
    "approved": _StatusEntry("green", ICON_SUCCESS),
    "passing": _StatusEntry("green", ICON_SUCCESS),
    # "open" is a GitHub API value; mapped green for PRs (positive).
    # For issues "open" means unresolved — acceptable approximation.
    "open": _StatusEntry("green", ICON_SUCCESS),
    # Failure / negative
    "failure": _StatusEntry("red", ICON_ERROR),
    "error": _StatusEntry("red", ICON_ERROR),
    "failed": _StatusEntry("red", ICON_ERROR),
    "changes_requested": _StatusEntry("red", ICON_ERROR),
    "conflicts": _StatusEntry("red", ICON_ERROR),
    "closed": _StatusEntry("red", ICON_ERROR),
    "cancelled": _StatusEntry("red", ICON_ERROR),
    "timed_out": _StatusEntry("red", ICON_ERROR),
    "startup_failure": _StatusEntry("red", ICON_ERROR),
    # Warning / in-progress
    "warning": _StatusEntry("yellow", ICON_WARNING),
    "draft": _StatusEntry("yellow", ICON_PENDING),
    "in_progress": _StatusEntry("yellow", ICON_PENDING),
    "pending": _StatusEntry("yellow", ICON_PENDING),
    "queued": _StatusEntry("yellow", ICON_PENDING),
    "action_required": _StatusEntry("yellow", ICON_WARNING),
    "stale": _StatusEntry("yellow", ICON_WARNING),
    "requested": _StatusEntry("yellow", ICON_PENDING),
    "waiting": _StatusEntry("yellow", ICON_PENDING),
    "review_required": _StatusEntry("yellow", ICON_PENDING),
    # Informational / neutral
    "info": _StatusEntry("blue", ICON_INFO),
    "skipped": _StatusEntry("dim", ICON_PENDING),
    "neutral": _StatusEntry("dim", ICON_PENDING),
    "dismissed": _StatusEntry("yellow", ICON_WARNING),
    "commented": _StatusEntry("blue", ICON_INFO),
}


def status_style(status: str) -> str:
    """Return the Rich style string for a status value, or 'default' if unknown.

    Lookup is case-insensitive — handles GitHub API mixed casing automatically.
    """
    entry = _STATUS_MAP.get(status.lower())
    return entry.style if entry else "default"


def status_icon(status: str) -> str:
    """Return the icon for a status value, or empty string if unknown.

    Lookup is case-insensitive — handles GitHub API mixed casing automatically.
    """
    entry = _STATUS_MAP.get(status.lower())
    return entry.icon if entry else ""
