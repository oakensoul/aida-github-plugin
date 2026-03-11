"""Tests for scripts/gh_api.py."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from scripts.gh_api import cmd_milestone_list, cmd_rulesets, main


class TestGhApiHelp:
    """Test argparse --help output."""

    @pytest.mark.parametrize("action", [
        "milestone-list", "milestone-create", "milestone-close",
        "milestone-edit", "milestone-delete", "rulesets",
    ])
    def test_help_exits_zero(self, action: str) -> None:
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_api.py", action, "--help"]
            main()
        assert exc_info.value.code == 0


class TestCmdMilestoneList:
    """Test the milestone-list subcommand."""

    @patch("subprocess.run")
    def test_milestone_list_json(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        repo_data = {"owner": {"login": "test-org"}, "name": "test-repo"}
        milestones = [
            {"number": 1, "title": "v1.0", "state": "open",
             "open_issues": 3, "closed_issues": 7, "due_on": "2026-06-01T00:00:00Z"},
        ]
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(repo_data), stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(milestones), stderr=""),
        ]
        import argparse
        args = argparse.Namespace(state="open", json=True)
        cmd_milestone_list(args)
        output = json.loads(capsys.readouterr().out)
        assert len(output) == 1
        assert output[0]["title"] == "v1.0"


class TestCmdRulesets:
    """Test the rulesets subcommand."""

    @patch("subprocess.run")
    def test_rulesets_json(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        repo_data = {"owner": {"login": "test-org"}, "name": "test-repo"}
        rulesets = [
            {"id": 1, "name": "protect-main", "enforcement": "active", "target": "branch"},
        ]
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(repo_data), stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(rulesets), stderr=""),
        ]
        import argparse
        args = argparse.Namespace(json=True)
        cmd_rulesets(args)
        output = json.loads(capsys.readouterr().out)
        assert output[0]["name"] == "protect-main"
