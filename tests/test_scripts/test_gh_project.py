"""Tests for scripts/gh_project.py."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from scripts.gh_project import cmd_list, cmd_status, main


class TestGhProjectHelp:
    """Test argparse --help output for all subcommands."""

    @pytest.mark.parametrize("action", ["status", "edit-field", "list", "add"])
    def test_help_exits_zero(self, action: str) -> None:
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_project.py", action, "--help"]
            main()
        assert exc_info.value.code == 0


class TestCmdList:
    """Test the list subcommand."""

    @patch("subprocess.run")
    def test_list_json(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        projects = {"projects": [{"number": 1, "title": "Board", "url": "https://example.com"}]}
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(projects), stderr=""
        )
        import argparse
        args = argparse.Namespace(owner="@me", json=True)
        cmd_list(args)
        output = json.loads(capsys.readouterr().out)
        assert len(output) == 1
        assert output[0]["title"] == "Board"


class TestCmdStatus:
    """Test the status subcommand."""

    @patch("subprocess.run")
    def test_status_json(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        items = {"items": [
            {"title": "Issue 1", "status": "Todo", "type": "ISSUE", "content": {"number": 1}},
            {"title": "Issue 2", "status": "Done", "type": "ISSUE", "content": {"number": 2}},
            {"title": "Issue 3", "status": "Todo", "type": "ISSUE", "content": {"number": 3}},
        ]}
        fields = {"fields": [
            {"name": "Status", "type": "SINGLE_SELECT", "options": [
                {"id": "1", "name": "Todo"}, {"id": "2", "name": "Done"},
            ]},
        ]}

        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(items), stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(fields), stderr=""),
        ]

        import argparse
        args = argparse.Namespace(
            owner="@me", project=5, group_by="Status", limit=200, json=True
        )
        cmd_status(args)
        output = json.loads(capsys.readouterr().out)
        assert output["totalCount"] == 3
        assert output["summary"]["Todo"] == 2
        assert output["summary"]["Done"] == 1
