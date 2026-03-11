#!/usr/bin/env python3
"""Release creation workflow.

Wraps the multi-step process: check latest tag, create tag, push, create release.
"""

from __future__ import annotations

import argparse

from utils.cli import run_gh, run_git
from utils.errors import ScriptError, die
from utils.output import print_json, print_success


def cmd_create(args: argparse.Namespace) -> None:
    """Create a GitHub release with tag."""
    tag = args.tag
    title = args.title or tag
    target = args.target or "HEAD"

    # Check if tag already exists
    result = run_git("tag", "--list", tag)
    if result.stdout.strip():
        die(ScriptError(
            f"Tag '{tag}' already exists",
            hint=f"Use a different tag or delete with: git tag -d {tag} && git push origin :refs/tags/{tag}",
        ))

    # Create and push tag
    if not args.no_tag:
        run_git("tag", "-a", tag, "-m", title, target)
        run_git("push", "origin", tag)

    # Create release
    gh_args = [
        "release", "create", tag,
        "--title", title,
        "--target", target,
    ]
    if args.notes:
        gh_args.extend(["--notes", args.notes])
    else:
        gh_args.append("--generate-notes")

    if args.draft:
        gh_args.append("--draft")
    if args.prerelease:
        gh_args.append("--prerelease")
    if args.latest is True:
        gh_args.append("--latest")
    elif args.latest is False:
        gh_args.append("--latest=false")

    result = run_gh(*gh_args)
    url = result.stdout.strip()
    print_success(f"Created release {tag}")

    if args.json:
        release_data = run_gh(
            "release", "view", tag,
            "--json", "tagName,name,isDraft,isPrerelease,url,createdAt",
            json_output=True,
        )
        print_json(release_data)
    elif url:
        print(url)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GitHub release creation workflow",
        prog="gh_release.py",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_create = sub.add_parser("create", help="Create a release")
    p_create.add_argument("tag", help="Tag name (e.g., v1.2.0)")
    p_create.add_argument("--title", help="Release title (default: tag name)")
    p_create.add_argument("--target", help="Target commitish (default: HEAD)")
    p_create.add_argument("--notes", help="Release notes text (default: auto-generated)")
    p_create.add_argument("--draft", action="store_true", help="Create as draft")
    p_create.add_argument("--prerelease", action="store_true", help="Mark as pre-release")
    p_create.add_argument("--latest", action=argparse.BooleanOptionalAction, default=None,
                           help="Mark as latest release")
    p_create.add_argument("--no-tag", action="store_true", help="Skip tag creation (tag must exist)")
    p_create.add_argument("--json", action="store_true", help="Output release data as JSON")

    args = parser.parse_args()
    actions = {"create": cmd_create}
    try:
        actions[args.action](args)
    except ScriptError as exc:
        die(exc)


if __name__ == "__main__":
    main()
