"""Tests for scripts/utils/cli.py subprocess wrappers."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from scripts.utils.cli import DEFAULT_TIMEOUT, get_repo_context, run_gh, run_git
from scripts.utils.errors import ScriptError


class TestRunGh:
    """Test run_gh subprocess wrapper."""

    @patch("subprocess.run")
    def test_basic_call(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="ok\n", stderr=""
        )
        result = run_gh("repo", "view")
        mock_run.assert_called_once_with(
            ["gh", "repo", "view"],
            capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=True,
        )
        assert result.stdout == "ok\n"

    @patch("subprocess.run")
    def test_json_output(self, mock_run: MagicMock) -> None:
        data = {"name": "test-repo"}
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(data), stderr=""
        )
        result = run_gh("repo", "view", "--json", "name", json_output=True)
        assert result == data

    @patch("subprocess.run")
    def test_timeout_raises_script_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["gh"], timeout=30)
        with pytest.raises(ScriptError, match="timed out"):
            run_gh("project", "list")

    @patch("subprocess.run")
    def test_called_process_error_maps_to_script_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["gh"], stderr="HTTP 404"
        )
        with pytest.raises(ScriptError, match="Not found"):
            run_gh("issue", "view", "999")

    @patch("subprocess.run")
    def test_json_parse_error_raises_script_error(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not valid json", stderr=""
        )
        with pytest.raises(ScriptError, match="Failed to parse JSON"):
            run_gh("repo", "view", json_output=True)

    @patch("subprocess.run")
    def test_custom_timeout(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        run_gh("pr", "list", timeout=60)
        mock_run.assert_called_once()
        assert mock_run.call_args.kwargs["timeout"] == 60


class TestRunGit:
    """Test run_git subprocess wrapper."""

    @patch("subprocess.run")
    def test_basic_call(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="main\n", stderr=""
        )
        result = run_git("rev-parse", "--abbrev-ref", "HEAD")
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=DEFAULT_TIMEOUT, check=True,
        )
        assert result.stdout == "main\n"

    @patch("subprocess.run")
    def test_timeout_raises_script_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["git"], timeout=30)
        with pytest.raises(ScriptError, match="timed out"):
            run_git("log", "--oneline")

    @patch("subprocess.run")
    def test_error_raises_script_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128, cmd=["git"], stderr="fatal: not a git repository"
        )
        with pytest.raises(ScriptError, match="not a git repository"):
            run_git("status")


class TestGetRepoContext:
    """Test get_repo_context."""

    @patch("subprocess.run")
    def test_returns_owner_and_repo(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=json.dumps({"owner": {"login": "oakensoul"}, "name": "my-repo"}),
            stderr="",
        )
        ctx = get_repo_context()
        assert ctx == {"owner": "oakensoul", "repo": "my-repo"}
