---
type: handler
name: release
title: Release Operations
description: Handler for /github release commands
skill: github
domain: release
version: 1.0.0
---

# /github release

## create

Create a GitHub release with auto-generated notes.

<!-- SCRIPT: scripts/gh_release.py create — multi-step: check tag, tag, push, create release -->

### Recommended

```bash
python scripts/gh_release.py create v1.0.0 --generate-notes
python scripts/gh_release.py create v2.0.0-rc.1 --prerelease --draft
```

Handles tag creation, push, and release creation in one step. Use `--no-tag` if the tag already exists.

### Quick Release

For a simple release from the latest tag:

```bash
gh release create v1.0.0 --generate-notes
```

### Full Release Flow

1. Check the latest tag:

```bash
git tag --sort=-creatordate | head -5
```

1. Determine the version bump (major/minor/patch) based on changes since last tag:

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

1. Create and push the tag:

```bash
git tag -a v<version> -m "Release v<version>"
git push origin v<version>
```

1. Create the release:

```bash
gh release create v<version> --generate-notes
```

### Options

| Flag | Purpose |
| ---- | ------- |
| `--generate-notes` | Auto-generate release notes from commits/PRs |
| `--draft` | Create as draft (not published) |
| `--prerelease` | Mark as pre-release |
| `--latest` | Mark as latest (default for non-prerelease) |
| `--title "..."` | Custom title (defaults to tag name) |
| `--notes "..."` | Custom release notes (instead of `--generate-notes`) |
| `--notes-file <path>` | Release notes from file |
| `--target <branch>` | Target branch (default: repo default) |

### With Assets

```bash
gh release create v1.0.0 dist/*.tar.gz dist/*.zip --generate-notes
```

### Pre-release

```bash
gh release create v2.0.0-rc.1 --prerelease --draft --generate-notes
```

## list

List releases.

```bash
# Recent releases
gh release list --limit 10

# JSON output
gh release list --json tagName,name,isPrerelease,publishedAt,isDraft
```

## tag

Create and push a git tag without a full release.

```bash
# Annotated tag (preferred)
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Push all tags
git push origin --tags
```

### Guardrails

- Always use **annotated tags** (`-a`) — lightweight tags lack metadata.
- Push tags explicitly — `git push` does not push tags by default.
- Never delete and recreate a tag that has been pushed — it breaks anyone who fetched it.

## view

View a specific release.

```bash
gh release view v1.0.0
gh release view v1.0.0 --json tagName,body,assets,publishedAt
```

## Reference

See [../references/release.md](../references/release.md) for version bump patterns, release notes
customization, and asset management.
