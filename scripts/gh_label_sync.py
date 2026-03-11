#!/usr/bin/env python3
"""Label sync and batch label operations.

Syncs repo labels against a standard taxonomy, and provides batch
add/remove operations with error handling.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from utils.cli import run_gh
from utils.errors import ScriptError, die
from utils.output import print_json, print_success

DATA_DIR = Path(__file__).parent / "data"


def cmd_sync(args: argparse.Namespace) -> None:
    """Sync repo labels against a standard taxonomy file."""
    taxonomy_path = Path(args.file) if args.file else DATA_DIR / "standard_labels.json"
    if not taxonomy_path.exists():
        die(ScriptError(
            f"Taxonomy file not found: {taxonomy_path}",
            hint="Provide --file or create scripts/data/standard_labels.json",
        ))

    with open(taxonomy_path) as f:
        taxonomy = json.load(f)

    existing = run_gh("label", "list", "--json", "name,color,description", "--limit", "200", json_output=True)
    existing_map = {label["name"].lower(): label for label in existing}

    created = []
    updated = []
    skipped = []

    for label_def in taxonomy:
        name = label_def["name"]
        color = label_def.get("color", "ededed")
        description = label_def.get("description", "")
        key = name.lower()

        if key not in existing_map:
            if not args.dry_run:
                gh_args = ["label", "create", name, "--color", color, "--force"]
                if description:
                    gh_args.extend(["--description", description])
                run_gh(*gh_args)
            created.append(name)
        else:
            current = existing_map[key]
            needs_update = (
                current.get("color", "").lower() != color.lower()
                or current.get("description", "") != description
            )
            if needs_update:
                if not args.dry_run:
                    gh_args = ["label", "edit", name, "--color", color,
                               "--description", description]
                    run_gh(*gh_args)
                updated.append(name)
            else:
                skipped.append(name)

    result = {"created": created, "updated": updated, "skipped": skipped}
    if args.json:
        result["dry_run"] = args.dry_run
        print_json(result)
    else:
        prefix = "[DRY RUN] " if args.dry_run else ""
        if created:
            print_success(f"{prefix}Created {len(created)} labels: {', '.join(created)}")
        if updated:
            print_success(f"{prefix}Updated {len(updated)} labels: {', '.join(updated)}")
        if skipped:
            print_success(f"{prefix}Skipped {len(skipped)} labels (already match)")


def cmd_add(args: argparse.Namespace) -> None:
    """Add a label to one or more issues/PRs."""
    errors = []
    for number in args.numbers:
        try:
            run_gh("issue", "edit", str(number), "--add-label", args.label)
            print_success(f"Added '{args.label}' to #{number}")
        except ScriptError as exc:
            errors.append({"number": number, "error": str(exc)})
    if errors:
        print_json({"errors": errors})
        die(f"Failed to add label to {len(errors)} item(s)")


def cmd_remove(args: argparse.Namespace) -> None:
    """Remove a label from one or more issues/PRs."""
    errors = []
    for number in args.numbers:
        try:
            run_gh("issue", "edit", str(number), "--remove-label", args.label)
            print_success(f"Removed '{args.label}' from #{number}")
        except ScriptError as exc:
            errors.append({"number": number, "error": str(exc)})
    if errors:
        print_json({"errors": errors})
        die(f"Failed to remove label from {len(errors)} item(s)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Label sync and batch label operations",
        prog="gh_label_sync.py",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # sync
    p_sync = sub.add_parser("sync", help="Sync labels against taxonomy")
    p_sync.add_argument("--file", help="Path to label taxonomy JSON (default: scripts/data/standard_labels.json)")
    p_sync.add_argument("--dry-run", action="store_true", help="Show what would change without making changes")
    p_sync.add_argument("--json", action="store_true", help="Output as JSON")

    # add
    p_add = sub.add_parser("add", help="Add label to issues/PRs")
    p_add.add_argument("--label", required=True, help="Label name to add")
    p_add.add_argument("numbers", type=int, nargs="+", help="Issue/PR numbers")

    # remove
    p_remove = sub.add_parser("remove", help="Remove label from issues/PRs")
    p_remove.add_argument("--label", required=True, help="Label name to remove")
    p_remove.add_argument("numbers", type=int, nargs="+", help="Issue/PR numbers")

    args = parser.parse_args()
    actions = {"sync": cmd_sync, "add": cmd_add, "remove": cmd_remove}
    try:
        actions[args.action](args)
    except ScriptError as exc:
        die(exc)


if __name__ == "__main__":
    main()
