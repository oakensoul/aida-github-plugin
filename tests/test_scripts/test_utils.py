"""Tests for scripts/utils/ modules."""

from __future__ import annotations

import subprocess

import pytest

from scripts.utils.errors import ScriptError, die, handle_gh_error
from scripts.utils.output import (
    print_diff_stat,
    print_error,
    print_info,
    print_items,
    print_json,
    print_section,
    print_status,
    print_success,
    print_table,
    print_warning,
)
from scripts.utils.style import (
    ICON_ERROR,
    ICON_INFO,
    ICON_PENDING,
    ICON_SUCCESS,
    ICON_WARNING,
    status_icon,
    status_style,
)


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

    def test_die_has_error_prefix(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            die("something broke")
        assert "error:" in capsys.readouterr().err

    def test_die_has_hint_prefix(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            die(ScriptError("failed", hint="do this"))
        captured = capsys.readouterr().err
        assert "hint:" in captured

    def test_die_string_has_no_hint(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            die("plain error")
        captured = capsys.readouterr().err
        assert "hint:" not in captured


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

    def test_print_table_has_separator(self, capsys: pytest.CaptureFixture[str]) -> None:
        rows = [{"name": "alice"}]
        print_table(rows, ["name"])
        output = capsys.readouterr().out
        assert "-----" in output


class TestPrintSuccess:
    """Test print_success with rich formatting."""

    def test_contains_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_success("deployed")
        assert "deployed" in capsys.readouterr().err

    def test_contains_ok_prefix(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_success("done")
        assert "ok:" in capsys.readouterr().err

    def test_contains_icon(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_success("done")
        assert ICON_SUCCESS in capsys.readouterr().err


class TestPrintError:
    """Test print_error with rich formatting."""

    def test_contains_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_error("connection failed")
        assert "connection failed" in capsys.readouterr().err

    def test_contains_error_prefix(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_error("bad")
        assert "error:" in capsys.readouterr().err

    def test_contains_icon(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_error("bad")
        assert ICON_ERROR in capsys.readouterr().err


class TestPrintWarning:
    """Test print_warning."""

    def test_contains_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_warning("check this")
        assert "check this" in capsys.readouterr().err

    def test_contains_warning_prefix(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_warning("caution")
        assert "warning:" in capsys.readouterr().err

    def test_contains_icon(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_warning("caution")
        assert ICON_WARNING in capsys.readouterr().err


class TestPrintInfo:
    """Test print_info."""

    def test_contains_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_info("fetching data")
        assert "fetching data" in capsys.readouterr().err

    def test_contains_icon(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_info("note")
        assert ICON_INFO in capsys.readouterr().err


class TestPrintStatus:
    """Test print_status label/value pairs."""

    def test_contains_label_and_value(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_status("State", "merged")
        captured = capsys.readouterr().err
        assert "State:" in captured
        assert "merged" in captured

    def test_unknown_status_still_renders(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_status("State", "unknown_value")
        captured = capsys.readouterr().err
        assert "State:" in captured
        assert "unknown_value" in captured


class TestPrintDiffStat:
    """Test print_diff_stat."""

    def test_shows_additions_and_deletions(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_diff_stat(42, 17)
        captured = capsys.readouterr().err
        assert "+42" in captured
        assert "-17" in captured

    def test_zero_values(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_diff_stat(0, 0)
        captured = capsys.readouterr().err
        assert "+0" in captured
        assert "-0" in captured


class TestPrintSection:
    """Test print_section."""

    def test_contains_title(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_section("Pull Requests")
        assert "Pull Requests" in capsys.readouterr().err


class TestPrintItems:
    """Test print_items bulleted list."""

    def test_contains_items(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_items(["first", "second", "third"])
        captured = capsys.readouterr().err
        assert "first" in captured
        assert "second" in captured
        assert "third" in captured

    def test_default_bullet(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_items(["item"])
        assert "- item" in capsys.readouterr().err

    def test_custom_bullet(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_items(["item"], bullet="*")
        assert "* item" in capsys.readouterr().err

    def test_empty_list(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_items([])
        assert capsys.readouterr().err == ""


class TestStyle:
    """Test style.py constants and functions."""

    # -- status_style --

    def test_status_style_success(self) -> None:
        assert status_style("success") == "green"
        assert status_style("merged") == "green"

    def test_status_style_failure(self) -> None:
        assert status_style("failure") == "red"
        assert status_style("error") == "red"

    def test_status_style_warning(self) -> None:
        assert status_style("warning") == "yellow"
        assert status_style("draft") == "yellow"

    def test_status_style_info(self) -> None:
        assert status_style("info") == "blue"

    def test_status_style_unknown(self) -> None:
        assert status_style("nonexistent") == "default"

    def test_status_style_case_insensitive(self) -> None:
        assert status_style("MERGED") == "green"
        assert status_style("Merged") == "green"
        assert status_style("OPEN") == "green"
        assert status_style("CLOSED") == "red"
        assert status_style("DRAFT") == "yellow"
        assert status_style("CHANGES_REQUESTED") == "red"

    # -- status_icon --

    def test_status_icon_success(self) -> None:
        assert status_icon("success") == ICON_SUCCESS

    def test_status_icon_failure(self) -> None:
        assert status_icon("failure") == ICON_ERROR

    def test_status_icon_warning(self) -> None:
        assert status_icon("warning") == ICON_WARNING

    def test_status_icon_pending(self) -> None:
        assert status_icon("pending") == ICON_PENDING

    def test_status_icon_info(self) -> None:
        assert status_icon("info") == ICON_INFO

    def test_status_icon_unknown(self) -> None:
        assert status_icon("nonexistent") == ""

    def test_status_icon_case_insensitive(self) -> None:
        assert status_icon("MERGED") == ICON_SUCCESS
        assert status_icon("OPEN") == ICON_SUCCESS
        assert status_icon("CLOSED") == ICON_ERROR
        assert status_icon("DRAFT") == ICON_PENDING
        assert status_icon("CHANGES_REQUESTED") == ICON_ERROR

    # -- GitHub API states coverage --

    def test_github_workflow_states(self) -> None:
        """Verify all GitHub workflow run states are mapped."""
        assert status_style("cancelled") == "red"
        assert status_style("timed_out") == "red"
        assert status_style("action_required") == "yellow"
        assert status_style("skipped") == "dim"
        assert status_style("neutral") == "dim"
        assert status_style("startup_failure") == "red"
        assert status_style("requested") == "yellow"
        assert status_style("waiting") == "yellow"

    def test_github_review_states(self) -> None:
        """Verify GitHub PR review states are mapped."""
        assert status_style("approved") == "green"
        assert status_style("changes_requested") == "red"
        assert status_style("review_required") == "yellow"
        assert status_style("dismissed") == "yellow"
        assert status_style("commented") == "blue"

    def test_draft_uses_pending_icon(self) -> None:
        """Draft is a pending state, not a warning — uses circle icon."""
        assert status_icon("draft") == ICON_PENDING
