"""Tests for scripts/utils/ modules."""

from __future__ import annotations

import subprocess

import pytest

from scripts.utils.errors import ScriptError, die, handle_gh_error
from scripts.utils.output import print_json, print_table


class TestScriptError:
    """Test ScriptError exception."""

    def test_basic_error(self) -> None:
        err = ScriptError("something broke")
        assert str(err) == "something broke"
        assert err.hint == ""

    def test_error_with_hint(self) -> None:
        err = ScriptError("permission denied", hint="Run: gh auth refresh")
        assert str(err) == "permission denied"
        assert err.hint == "Run: gh auth refresh"


class TestHandleGhError:
    """Test handle_gh_error mapping."""

    def test_oauth_scope_error(self) -> None:
        exc = subprocess.CalledProcessError(
            returncode=4, cmd=["gh"], stderr="insufficient OAuth scopes"
        )
        result = handle_gh_error(exc)
        assert "Permission denied" in str(result)
        assert "gh auth refresh" in result.hint

    def test_404_error(self) -> None:
        exc = subprocess.CalledProcessError(
            returncode=1, cmd=["gh"], stderr="HTTP 404"
        )
        result = handle_gh_error(exc)
        assert "Not found" in str(result)

    def test_422_error(self) -> None:
        exc = subprocess.CalledProcessError(
            returncode=1, cmd=["gh"], stderr="HTTP 422: Validation Failed"
        )
        result = handle_gh_error(exc)
        assert "Validation failed" in str(result)

    def test_403_error(self) -> None:
        exc = subprocess.CalledProcessError(
            returncode=1, cmd=["gh"], stderr="HTTP 403: Forbidden"
        )
        result = handle_gh_error(exc)
        assert "Forbidden" in str(result)

    def test_generic_error(self) -> None:
        exc = subprocess.CalledProcessError(
            returncode=1, cmd=["gh"], stderr="something unexpected"
        )
        result = handle_gh_error(exc)
        assert "exit 1" in str(result)

    def test_project_scope_guess(self) -> None:
        exc = subprocess.CalledProcessError(
            returncode=4, cmd=["gh"], stderr="insufficient OAuth scopes for project"
        )
        result = handle_gh_error(exc)
        assert "project" in result.hint


class TestDie:
    """Test die() exit behavior."""

    def test_die_with_string(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc_info:
            die("bad thing happened")
        assert exc_info.value.code == 1
        assert "bad thing happened" in capsys.readouterr().err

    def test_die_with_script_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc_info:
            die(ScriptError("failed", hint="try this"))
        assert exc_info.value.code == 1
        captured = capsys.readouterr().err
        assert "failed" in captured
        assert "try this" in captured

    def test_die_custom_code(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            die("usage error", code=2)
        assert exc_info.value.code == 2


class TestOutput:
    """Test output formatting."""

    def test_print_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_json({"key": "value"})
        output = capsys.readouterr().out
        assert '"key": "value"' in output

    def test_print_table_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_table([], ["a", "b"])
        assert "(no results)" in capsys.readouterr().out

    def test_print_table_with_data(self, capsys: pytest.CaptureFixture[str]) -> None:
        rows = [{"name": "alice", "age": 30}, {"name": "bob", "age": 25}]
        print_table(rows, ["name", "age"])
        output = capsys.readouterr().out
        assert "NAME" in output
        assert "alice" in output
        assert "bob" in output
