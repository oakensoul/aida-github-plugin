"""Validate plugin file structure and required files exist."""

import json
import re
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

    def test_skill_handler_files_exist(self, project_root: Path) -> None:
        handlers_dir = project_root / "skills" / "github" / "handlers"
        assert handlers_dir.exists(), "handlers/ directory is required"
        expected = [
            "pr.md", "branch.md", "issue.md", "project.md",
            "release.md", "label.md", "milestone.md",
            "actions.md", "repo.md", "search.md",
        ]
        for filename in expected:
            assert (handlers_dir / filename).exists(), f"handlers/{filename} is required"

    def test_handler_frontmatter_valid(self, project_root: Path) -> None:
        handlers_dir = project_root / "skills" / "github" / "handlers"
        for handler_file in sorted(handlers_dir.glob("*.md")):
            content = handler_file.read_text()
            assert content.startswith("---"), f"{handler_file.name} must have frontmatter"
            end = content.index("---", 3)
            frontmatter = content[3:end]
            assert "type: handler" in frontmatter, f"{handler_file.name} must have type: handler"
            assert "domain:" in frontmatter, f"{handler_file.name} must have domain field"
            assert "skill: github" in frontmatter, f"{handler_file.name} must have skill: github"

    def test_handler_domain_matches_filename(self, project_root: Path) -> None:
        handlers_dir = project_root / "skills" / "github" / "handlers"
        for handler_file in sorted(handlers_dir.glob("*.md")):
            content = handler_file.read_text()
            expected_domain = handler_file.stem
            assert f"domain: {expected_domain}" in content, \
                f"{handler_file.name} domain field must match filename '{expected_domain}'"

    def test_routing_table_matches_handlers(self, project_root: Path) -> None:
        skill_md = project_root / "skills" / "github" / "SKILL.md"
        content = skill_md.read_text()
        routing_domains = set(re.findall(r"\| `(\w+)` \|", content))
        handler_files = {f.stem for f in (project_root / "skills" / "github" / "handlers").glob("*.md")}
        missing_handlers = routing_domains - handler_files
        missing_routes = handler_files - routing_domains
        assert not missing_handlers, f"Routing table references missing handlers: {missing_handlers}"
        assert not missing_routes, f"Handler files missing from routing table: {missing_routes}"

    def test_help_menu_covers_routing_table_actions(self, project_root: Path) -> None:
        skill_md = project_root / "skills" / "github" / "SKILL.md"
        content = skill_md.read_text()
        help_start = content.index("```text")
        help_end = content.index("```", help_start + 1)
        help_menu = content[help_start:help_end]
        help_actions = set(re.findall(r"/github (\w+ \w+)", help_menu))
        routing_rows = re.findall(r"\| `(\w+)` \|[^|]+\| (`.+`) \|", content)
        routing_actions = set()
        for domain, actions_str in routing_rows:
            for action in re.findall(r"`(\w+)`", actions_str):
                routing_actions.add(f"{domain} {action}")
        missing = routing_actions - help_actions
        assert not missing, f"Actions in routing table but missing from help menu: {missing}"

    def test_scripts_directory_structure(self, project_root: Path) -> None:
        scripts_dir = project_root / "scripts"
        assert (scripts_dir / "__init__.py").exists(), "scripts/__init__.py is required"
        assert (scripts_dir / "utils" / "__init__.py").exists(), "scripts/utils/__init__.py is required"
        expected_utils = ["cli.py", "output.py", "errors.py"]
        for filename in expected_utils:
            assert (scripts_dir / "utils" / filename).exists(), f"scripts/utils/{filename} is required"

    def test_script_files_exist(self, project_root: Path) -> None:
        scripts_dir = project_root / "scripts"
        expected = [
            "gh_project.py", "gh_query.py", "gh_label_sync.py",
            "gh_api.py", "gh_pr_body.py", "gh_release.py",
        ]
        for filename in expected:
            assert (scripts_dir / filename).exists(), f"scripts/{filename} is required"

    def test_script_data_files_exist(self, project_root: Path) -> None:
        data_dir = project_root / "scripts" / "data"
        assert (data_dir / "standard_labels.json").exists(), "standard_labels.json is required"

    def test_script_templates_exist(self, project_root: Path) -> None:
        templates_dir = project_root / "scripts" / "templates"
        expected = ["pr_default.md.j2", "pr_bugfix.md.j2", "issue_default.md.j2", "issue_bug.md.j2"]
        for filename in expected:
            assert (templates_dir / filename).exists(), f"templates/{filename} is required"

    def test_handler_script_markers_reference_existing_scripts(self, project_root: Path) -> None:
        handlers_dir = project_root / "skills" / "github" / "handlers"
        for handler_file in sorted(handlers_dir.glob("*.md")):
            content = handler_file.read_text()
            for line in content.splitlines():
                if "<!-- SCRIPT:" in line:
                    # Extract script path from marker
                    script_ref = line.split("<!-- SCRIPT:")[1].split("—")[0].strip()
                    script_path = script_ref.split()[0]  # e.g., "scripts/gh_project.py"
                    assert (project_root / script_path).exists(), \
                        f"{handler_file.name} references non-existent script: {script_path}"

    def test_adr_files_exist(self, project_root: Path) -> None:
        adr_dir = project_root / "docs" / "architecture" / "adr"
        assert adr_dir.exists(), "ADR directory is required"
        adrs = list(adr_dir.glob("[0-9]*.md"))
        assert len(adrs) >= 6, f"Expected at least 6 ADRs, found {len(adrs)}"
