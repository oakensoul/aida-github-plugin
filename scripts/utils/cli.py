"""Subprocess wrappers for gh and git CLI commands."""

from __future__ import annotations

import json
import subprocess
from typing import Any

from .errors import ScriptError, handle_gh_error

DEFAULT_TIMEOUT = 30


def run_gh(
    *args: str,
    json_output: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> subprocess.CompletedProcess[str] | Any:
    """Run a gh CLI command and return the result.

    When json_output=True, parses stdout as JSON and returns the parsed object.
    Otherwise returns the CompletedProcess for the caller to inspect.
    """
    cmd = ["gh", *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise ScriptError(
            f"Command timed out after {timeout}s: {' '.join(cmd)}",
            hint="Try increasing --timeout or narrowing the query.",
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise handle_gh_error(exc) from exc

    if json_output:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ScriptError(
                f"Failed to parse JSON from gh output: {result.stdout[:200]}",
                hint="The gh command succeeded but returned unexpected output.",
            ) from exc
    return result


def run_git(
    *args: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the CompletedProcess."""
    cmd = ["git", *args]
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise ScriptError(
            f"Command timed out after {timeout}s: {' '.join(cmd)}",
            hint="Try increasing --timeout.",
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise ScriptError(f"git failed (exit {exc.returncode}): {stderr}") from exc


def get_repo_context() -> dict[str, str]:
    """Return owner and repo name from the current git remote."""
    result = run_gh("repo", "view", "--json", "owner,name", json_output=True)
    return {"owner": result["owner"]["login"], "repo": result["name"]}
