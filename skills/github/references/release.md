---
type: reference
title: "Release and Tag Recipes"
description: "Operational recipes for GitHub releases, tags, and version bump workflows via gh and git CLI"
skill: github
category: releases
version: 1.0.0
---

# Release and Tag Recipes

Lean recipe reference for `gh release` and `git tag` operations. Organized by task.

## Recipes

### 1. Create Release with Auto-Generated Notes

```bash
gh release create v1.2.0 --generate-notes --title "v1.2.0"
```

Generates a changelog from merged PRs since the previous tag. Requires at least one prior tag.

### 2. Create with Specific Range

```bash
gh release create v1.2.0 --generate-notes --notes-start-tag v1.1.0 --title "v1.2.0"
```

Use `--notes-start-tag` to control exactly which commits appear in the auto-generated notes. Essential when
tags are not sequential or you skipped a release.

### 3. Create Pre-Release or Draft

```bash
# Draft pre-release (not visible to users, marked as pre-release)
gh release create v2.0.0-rc.1 --prerelease --draft --generate-notes --title "v2.0.0-rc.1"

# Published pre-release (visible but marked as pre-release)
gh release create v2.0.0-rc.1 --prerelease --generate-notes --title "v2.0.0-rc.1"
```

### 4. Create with Assets

```bash
gh release create v1.2.0 --generate-notes --title "v1.2.0" \
  dist/*.tar.gz \
  "docs/guide.pdf#User Guide"
```

Assets are positional arguments after the tag. Append `#label` to set the display name shown in the GitHub UI.

### 5. Create Targeting a Specific Branch

```bash
gh release create v1.2.0 --target release/1.2 --generate-notes --title "v1.2.0"
```

Default target is the repo's default branch. Use `--target` for release branches or hotfix branches.

### 6. List Releases

```bash
# Recent releases
gh release list --limit 10

# JSON output for scripting
gh release list --json tagName,name,isDraft,isPrerelease,publishedAt --limit 20
```

### 7. View Release

```bash
# Human-readable
gh release view v1.2.0

# JSON for specific fields
gh release view v1.2.0 --json tagName,body,assets,publishedAt,isPrerelease,isDraft
```

### 8. Edit Release

```bash
# Promote draft to published
gh release edit v1.2.0 --draft=false

# Update title and notes
gh release edit v1.2.0 --title "v1.2.0 - Stability Release" --notes "Updated changelog..."

# Demote to pre-release
gh release edit v1.2.0 --prerelease
```

### 9. Delete Release

```bash
# Delete release only (keeps the tag)
gh release delete v1.2.0 --yes

# Delete release and its tag
gh release delete v1.2.0 --yes --cleanup-tag
```

### 10. Download Assets

```bash
# All assets
gh release download v1.2.0

# Filter by pattern
gh release download v1.2.0 --pattern "*.tar.gz"

# Download to specific directory
gh release download v1.2.0 --pattern "*.tar.gz" --dir ./artifacts
```

## Tag Operations

### Create Annotated Tag

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
```

Annotated tags (`-a`) store author, date, and message. Always use annotated tags for releases.

### Push Tags

```bash
# Push a specific tag
git push origin v1.2.0

# Push all local tags
git push origin --tags
```

### List Tags

```bash
# List by creation date (newest first)
git tag --sort=-creatordate | head -20

# List with annotation messages
git tag -n --sort=-creatordate | head -20
```

### Delete Tags

```bash
# Delete local tag
git tag -d v1.2.0-bad

# Delete remote tag
git push origin --delete v1.2.0-bad
```

## Version Bump Pattern

Standard workflow for cutting a new release.

```bash
# 1. Check latest release
gh release list --limit 1

# 2. View commits since last tag
git log --oneline v1.1.0..HEAD

# 3. Decide bump level (major/minor/patch) based on changes

# 4. Create and push annotated tag
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 5. Create release with scoped notes
gh release create v1.2.0 --generate-notes --notes-start-tag v1.1.0 --title "v1.2.0"
```

Always push the tag before creating the release. This ensures the tag exists remotely and avoids
`gh release create` creating a lightweight tag automatically.

## Gotchas

- **`--verify-tag`:** Aborts release creation if the tag does not already exist on the remote. Use in CI
  pipelines as a safety gate to ensure the tag was pushed deliberately.
- **`--fail-on-no-commits`:** Prevents creating empty releases when no changes landed since the start tag.
  Useful in automated release scripts.
- **Annotated vs lightweight tags:** Annotated tags (`git tag -a`) store metadata and are preferred for
  releases. Lightweight tags (`git tag v1.0.0` without `-a`) are for temporary markers and bookmarks.
- **Push tag before release:** Always `git push origin <tag>` before `gh release create`. If the tag does not
  exist remotely, `gh release create` creates a lightweight tag, which lacks author and date metadata.
- **`--notes-start-tag` scope:** Controls the starting point for auto-generated notes. Without it, GitHub uses
  the previous tag by semver order, which may not be what you want after hotfix branches or skipped versions.
- **Draft visibility:** Draft releases are invisible to non-collaborators. Use drafts for internal review
  before publishing with `gh release edit <tag> --draft=false`.

## Go Deeper

- [gh release](https://cli.github.com/manual/gh_release)
- [gh release create](https://cli.github.com/manual/gh_release_create)
- [gh release edit](https://cli.github.com/manual/gh_release_edit)
- [gh release download](https://cli.github.com/manual/gh_release_download)
