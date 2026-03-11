"""Validate plugin file structure and required files exist."""

import json
from pathlib import Path


class TestPluginStructure:
    """Verify required plugin files exist and are valid."""

    def test_plugin_json_exists(self, project_root: Path) -> None:
        plugin_json = project_root / ".claude-plugin" / "plugin.json"
        assert plugin_json.exists(), "plugin.json is required"

    def test_plugin_json_valid(self, project_root: Path) -> None:
        plugin_json = project_root / ".claude-plugin" / "plugin.json"
        data = json.loads(plugin_json.read_text())
        assert "name" in data
        assert "version" in data

    def test_aida_config_exists(self, project_root: Path) -> None:
        config = project_root / ".claude-plugin" / "aida-config.json"
        assert config.exists(), "aida-config.json is required"

    def test_aida_config_valid(self, project_root: Path) -> None:
        config = project_root / ".claude-plugin" / "aida-config.json"
        data = json.loads(config.read_text())
        assert "agents" in data
        assert "skills" in data
        assert "github-expert" in data["agents"]
        assert "github" in data["skills"]

    def test_agent_definition_exists(self, project_root: Path) -> None:
        agent = project_root / "agents" / "github-expert" / "github-expert.md"
        assert agent.exists(), "github-expert agent definition is required"

    def test_agent_knowledge_files_exist(self, project_root: Path) -> None:
        knowledge_dir = project_root / "agents" / "github-expert" / "knowledge"
        expected = ["index.md", "operations.md", "guardrails.md", "decisions.md"]
        for filename in expected:
            assert (knowledge_dir / filename).exists(), f"knowledge/{filename} is required"

    def test_skill_definition_exists(self, project_root: Path) -> None:
        skill = project_root / "skills" / "github" / "SKILL.md"
        assert skill.exists(), "github SKILL.md is required"

    def test_skill_reference_files_exist(self, project_root: Path) -> None:
        refs_dir = project_root / "skills" / "github" / "references"
        expected = [
            "pr.md", "issue.md", "project.md", "repo.md", "actions.md",
            "release.md", "branching.md", "rebase-and-merge.md", "recovery.md",
        ]
        for filename in expected:
            assert (refs_dir / filename).exists(), f"references/{filename} is required"

    def test_adr_files_exist(self, project_root: Path) -> None:
        adr_dir = project_root / "docs" / "architecture" / "adr"
        assert adr_dir.exists(), "ADR directory is required"
        adrs = list(adr_dir.glob("[0-9]*.md"))
        assert len(adrs) >= 6, f"Expected at least 6 ADRs, found {len(adrs)}"
