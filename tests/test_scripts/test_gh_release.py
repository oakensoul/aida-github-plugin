"""Tests for scripts/gh_release.py."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from scripts.gh_release import main


class TestGhReleaseHelp:
    """Test argparse --help output."""

    def test_create_help_exits_zero(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_release.py", "create", "--help"]
            main()
        assert exc_info.value.code == 0


class TestCmdCreate:
    """Test the create subcommand."""

    @patch("subprocess.run")
    def test_create_fails_if_tag_exists(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="v1.0.0\n", stderr=""
        )
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_release.py", "create", "v1.0.0"]
            main()
        assert exc_info.value.code == 1

    @patch("subprocess.run")
    def test_create_success(self, mock_run: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
        # Call sequence: git tag --list (empty), git tag -a, git push, gh release create
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),   # tag --list
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),   # tag -a
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),   # push
            subprocess.CompletedProcess(                                                  # release create
                args=[], returncode=0, stdout="https://github.com/test/repo/releases/v1.0.0\n", stderr=""
            ),
        ]
        import sys
        sys.argv = ["gh_release.py", "create", "v1.0.0"]
        main()
        output = capsys.readouterr()
        assert "v1.0.0" in output.out or "v1.0.0" in output.err
