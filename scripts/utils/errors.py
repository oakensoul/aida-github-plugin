"""Error types and error handling for gh/git subprocess calls."""

from __future__ import annotations

import subprocess
import sys
from typing import NoReturn

from rich.text import Text

from .output import print_error, status_console
from .style import ICON_INFO


class ScriptError(Exception):
    """An error with an actionable hint for the user."""

    def __init__(self, message: str, *, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint


def handle_gh_error(exc: subprocess.CalledProcessError) -> ScriptError:
    """Map common gh CLI errors to actionable ScriptError messages."""
    stderr = (exc.stderr or "").strip()

    if exc.returncode == 4 or "insufficient OAuth scopes" in stderr:
        scope = _guess_scope(stderr)
        return ScriptError(
            f"Permission denied: {stderr}",
            hint=f"Run: gh auth refresh -s {scope}",
        )

    if "HTTP 404" in stderr or "Could not resolve" in stderr:
        return ScriptError(
            f"Not found: {stderr}",
            hint="Check the owner, repo, and resource ID.",
        )

    if "HTTP 422" in stderr:
        return ScriptError(
            f"Validation failed: {stderr}",
            hint="Check required fields and value constraints.",
        )

    if "HTTP 403" in stderr:
        return ScriptError(
            f"Forbidden: {stderr}",
            hint="Check repository permissions and authentication.",
        )

    return ScriptError(f"gh failed (exit {exc.returncode}): {stderr}")


def die(error: ScriptError | str, *, code: int = 1) -> NoReturn:
    """Print an error (and optional hint) to stderr with color, then exit."""
    print_error(str(error))
    if isinstance(error, ScriptError) and error.hint:
        hint_text = Text()
        hint_text.append(f"{ICON_INFO} ", style="yellow")
        hint_text.append("hint: ", style="yellow bold")
        hint_text.append(error.hint)
        status_console().print(hint_text)
    sys.exit(code)


def _guess_scope(stderr: str) -> str:
    """Guess the missing OAuth scope from the error message."""
    if "project" in stderr.lower():
        return "project"
    if "admin" in stderr.lower():
        return "admin:org"
    return "repo"
