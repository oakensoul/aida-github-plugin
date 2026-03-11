"""Tests for scripts/gh_label_sync.py."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.gh_label_sync import cmd_sync, main


class TestGhLabelSyncHelp:
    """Test argparse --help output."""

    @pytest.mark.parametrize("action", ["sync", "add", "remove"])
    def test_help_exits_zero(self, action: str) -> None:
        with pytest.raises(SystemExit) as exc_info:
            import sys
            sys.argv = ["gh_label_sync.py", action, "--help"]
            main()
        assert exc_info.value.code == 0


class TestCmdSync:
    """Test the sync subcommand."""

    @patch("subprocess.run")
    def test_sync_dry_run(
        self, mock_run: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        taxonomy = [
            {"name": "bug", "color": "d73a4a", "description": "Something broken"},
            {"name": "new-label", "color": "0075ca", "description": "Brand new"},
        ]
        taxonomy_file = tmp_path / "labels.json"
        taxonomy_file.write_text(json.dumps(taxonomy))

        existing = [{"name": "bug", "color": "d73a4a", "description": "Something broken"}]
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(existing), stderr=""
        )

        import argparse
        args = argparse.Namespace(file=str(taxonomy_file), dry_run=True, json=True)
        cmd_sync(args)
        output = json.loads(capsys.readouterr().out)
        assert "new-label" in output["created"]
        assert "bug" in output["skipped"]
        assert output["dry_run"] is True

    @patch("subprocess.run")
    def test_sync_creates_missing(
        self, mock_run: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        taxonomy = [{"name": "feature", "color": "a2eeef", "description": "New feature"}]
        taxonomy_file = tmp_path / "labels.json"
        taxonomy_file.write_text(json.dumps(taxonomy))

        existing: list = []
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(existing), stderr=""
        )

        import argparse
        args = argparse.Namespace(file=str(taxonomy_file), dry_run=False, json=True)
        cmd_sync(args)
        output = json.loads(capsys.readouterr().out)
        assert "feature" in output["created"]
        # One call for list, one for create
        assert mock_run.call_count == 2


class TestStandardLabelsFile:
    """Test that the standard labels data file is valid."""

    def test_standard_labels_json_valid(self) -> None:
        labels_file = Path(__file__).parent.parent.parent / "scripts" / "data" / "standard_labels.json"
        assert labels_file.exists(), "standard_labels.json must exist"
        labels = json.loads(labels_file.read_text())
        assert isinstance(labels, list)
        assert len(labels) > 0
        for label in labels:
            assert "name" in label, f"Label missing 'name': {label}"
            assert "color" in label, f"Label missing 'color': {label}"
            assert len(label["color"]) == 6, f"Color must be 6 hex chars: {label}"
