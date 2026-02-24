---
type: documentation
title: Aida Github Plugin
---

# Aida Github Plugin

AIDA plugin with agents and skills for GitHub operations including CI/CD, releases, and repository management

## Project Structure

```text
aida-github-plugin/
├── .claude-plugin/       # Plugin metadata
│   ├── plugin.json       # Required plugin manifest
│   ├── marketplace.json  # Marketplace listing
│   └── aida-config.json  # AIDA configuration
├── agents/               # Agent definitions
├── skills/               # Skill definitions
├── scripts/              # Python scripts
├── tests/                # Test suite
├── pyproject.toml        # Python project config
├── docs/                 # Documentation
└── Makefile              # Build targets
```

## Development

### Commands

```bash
make lint          # Run all linters
make test          # Run tests
make clean         # Remove build artifacts
```

### Python Setup

```bash
pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/ -v
```

## Conventions

### Markdown

- YAML frontmatter required (type, name, description, version)
- Line length: 120 characters

## Key Files

- `.claude-plugin/plugin.json` - Plugin manifest
- `CLAUDE.md` - Project instructions for Claude Code
