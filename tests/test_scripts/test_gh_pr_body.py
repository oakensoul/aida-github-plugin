"""Tests for scripts/gh_pr_body.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.gh_pr_body import cmd_list, cmd_render, main


class TestGhPrBodyHelp:
    """Test argparse --help output."""

    @pytest.mark.parametrize("action", ["render", "list"])
    def test_help_exits_zero(self, action: str) -> None:
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_pr_body.py", action, "--help"]
            main()
        assert exc_info.value.code == 0


class TestCmdList:
    """Test the list subcommand."""

    def test_list_builtin_templates(self, capsys: pytest.CaptureFixture[str]) -> None:
        import argparse
        args = argparse.Namespace(template_dir=None)
        cmd_list(args)
        output = capsys.readouterr().out
        assert "pr_default.md.j2" in output
        assert "issue_bug.md.j2" in output


class TestCmdRender:
    """Test the render subcommand."""

    def test_render_pr_default(self, capsys: pytest.CaptureFixture[str]) -> None:
        import argparse
        args = argparse.Namespace(
            template_dir=None,
            template="pr_default.md.j2",
            var=["summary=Fix authentication bug", "issue=42"],
        )
        # Mock git/gh calls in _build_context
        with patch("scripts.gh_pr_body.run_git") as mock_git, \
             patch("scripts.gh_pr_body.get_repo_context") as mock_ctx, \
             patch("scripts.gh_pr_body.run_gh") as mock_gh:
            import subprocess
            mock_git.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="fix/42\n", stderr=""
            )
            mock_ctx.return_value = {"owner": "test", "repo": "test-repo"}
            mock_gh.return_value = {"login": "testuser"}
            cmd_render(args)

        output = capsys.readouterr().out
        assert "Fix authentication bug" in output
        assert "Closes #42" in output

    def test_render_missing_template(self) -> None:
        import argparse
        args = argparse.Namespace(
            template_dir=None,
            template="nonexistent.md.j2",
            var=None,
        )
        with patch("scripts.gh_pr_body.run_git"), \
             patch("scripts.gh_pr_body.get_repo_context"), \
             patch("scripts.gh_pr_body.run_gh"):
            with pytest.raises(SystemExit):
                cmd_render(args)


class TestTemplateFiles:
    """Test that template files are valid Jinja2."""

    def test_all_templates_parse(self) -> None:
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        templates_dir = Path(__file__).parent.parent.parent / "scripts" / "templates"
        assert templates_dir.exists()
        env = SandboxedEnvironment(loader=FileSystemLoader(str(templates_dir)))
        for template_file in templates_dir.glob("*.j2"):
            template = env.get_template(template_file.name)
            assert template is not None, f"Failed to parse {template_file.name}"
