"""Shared fixtures for script tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def scripts_dir() -> Path:
    """Return the scripts directory path."""
    return Path(__file__).parent.parent.parent / "scripts"
