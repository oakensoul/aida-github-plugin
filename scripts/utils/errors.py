"""Error types and error handling for gh/git subprocess calls."""

from __future__ import annotations

import subprocess
import sys
from typing import NoReturn


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
    """Print an error (and optional hint) to stderr, then exit."""
    if isinstance(error, ScriptError):
        print(f"error: {error}", file=sys.stderr)
        if error.hint:
            print(f"hint: {error.hint}", file=sys.stderr)
    else:
        print(f"error: {error}", file=sys.stderr)
    sys.exit(code)


def _guess_scope(stderr: str) -> str:
    """Guess the missing OAuth scope from the error message."""
    if "project" in stderr.lower():
        return "project"
    if "admin" in stderr.lower():
        return "admin:org"
    return "repo"
