"""Tests for scripts/gh_query.py."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from scripts.gh_query import cmd_issues, cmd_prs, cmd_runs, main


class TestGhQueryHelp:
    """Test argparse --help output for all subcommands."""

    @pytest.mark.parametrize("action", ["prs", "issues", "runs", "checks"])
    def test_help_exits_zero(self, action: str) -> None:
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_query.py", action, "--help"]
            main()
        assert exc_info.value.code == 0


class TestCmdPrs:
    """Test the prs subcommand."""

    @patch("subprocess.run")
    def test_prs_json(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        prs = [
            {"number": 1, "title": "Fix bug", "state": "OPEN", "author": {"login": "dev"},
             "labels": [{"name": "bug"}], "headRefName": "fix/1", "url": "https://example.com/1",
             "isDraft": False, "reviewDecision": "APPROVED", "statusCheckRollup": []},
        ]
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(prs), stderr=""
        )
        import argparse
        args = argparse.Namespace(
            state=None, label=None, author=None, base=None, search=None, limit=30, json=True
        )
        cmd_prs(args)
        output = json.loads(capsys.readouterr().out)
        assert len(output) == 1
        assert output[0]["number"] == 1


class TestCmdIssues:
    """Test the issues subcommand."""

    @patch("subprocess.run")
    def test_issues_table(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        issues = [
            {"number": 42, "title": "Auth broken", "state": "OPEN",
             "labels": [{"name": "bug"}], "assignees": [], "milestone": {"title": "v1.0"},
             "url": "https://example.com/42", "createdAt": "2026-01-01"},
        ]
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(issues), stderr=""
        )
        import argparse
        args = argparse.Namespace(
            state=None, label=None, assignee=None, milestone=None, search=None, limit=30, json=False
        )
        cmd_issues(args)
        output = capsys.readouterr().out
        assert "#42" in output
        assert "Auth broken" in output


class TestCmdRuns:
    """Test the runs subcommand."""

    @patch("subprocess.run")
    def test_runs_json(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        runs = [
            {"databaseId": 100, "displayTitle": "CI", "status": "completed",
             "conclusion": "success", "event": "push", "headBranch": "main",
             "url": "https://example.com/100", "createdAt": "2026-01-01"},
        ]
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(runs), stderr=""
        )
        import argparse
        args = argparse.Namespace(
            branch=None, status=None, workflow=None, limit=20, json=True
        )
        cmd_runs(args)
        output = json.loads(capsys.readouterr().out)
        assert output[0]["status"] == "completed"
