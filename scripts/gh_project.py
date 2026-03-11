#!/usr/bin/env python3
"""GitHub Projects v2 operations — status, edit-field, list, add.

Wraps the multi-step ID lookup dance required for project field edits.
Requires the `project` OAuth scope: gh auth refresh -s project
"""

from __future__ import annotations

import argparse
import sys

from utils.cli import run_gh
from utils.errors import ScriptError, die
from utils.output import print_json, print_success, print_table

DEFAULT_LIMIT = 200  # gh project item-list defaults to 30, which truncates


def cmd_status(args: argparse.Namespace) -> None:
    """Show project board status with item counts by field value."""
    owner = args.owner
    project_number = args.project

    items = run_gh(
        "project", "item-list", str(project_number),
        "--owner", owner,
        "--format", "json",
        "--limit", str(args.limit),
        json_output=True,
    )

    fields = run_gh(
        "project", "field-list", str(project_number),
        "--owner", owner,
        "--format", "json",
        json_output=True,
    )

    status_field = None
    for field in fields.get("fields", []):
        if field["name"].lower() == args.group_by.lower():
            status_field = field
            break

    item_list = items.get("items", [])

    # Build counts once if we have a groupable field
    counts: dict[str, int] | None = None
    if status_field and status_field.get("options"):
        counts = {}
        for item in item_list:
            val = _get_field_value(item, args.group_by)
            counts[val] = counts.get(val, 0) + 1

    if args.json:
        result = {
            "totalCount": len(item_list),
            "items": item_list,
        }
        if counts is not None:
            result["summary"] = counts
        print_json(result)
    else:
        if counts is not None:
            rows = [{"status": k, "count": v} for k, v in sorted(counts.items())]
            print_table(rows, ["status", "count"])
            print(f"\nTotal: {len(item_list)}", file=sys.stderr)
        else:
            rows = []
            for item in item_list:
                row = {
                    "title": item.get("title", ""),
                    "type": item.get("type", ""),
                    "status": _get_field_value(item, "Status"),
                }
                if item.get("content", {}).get("number"):
                    row["number"] = f"#{item['content']['number']}"
                rows.append(row)
            print_table(rows, ["number", "title", "type", "status"])


def cmd_edit_field(args: argparse.Namespace) -> None:
    """Edit a project item field by human-readable names (eliminates the 4-step ID dance)."""
    owner = args.owner
    project_number = args.project

    # Step 1: Get project ID
    projects = run_gh(
        "project", "list",
        "--owner", owner,
        "--format", "json",
        json_output=True,
    )
    project_id = None
    for proj in projects.get("projects", []):
        if proj.get("number") == project_number:
            project_id = proj["id"]
            break
    if not project_id:
        die(ScriptError(
            f"Project #{project_number} not found for owner '{owner}'",
            hint=f"Run: gh project list --owner {owner} --format json",
        ))

    # Step 2: Get field ID and option IDs
    fields = run_gh(
        "project", "field-list", str(project_number),
        "--owner", owner,
        "--format", "json",
        json_output=True,
    )
    target_field = None
    for field in fields.get("fields", []):
        if field["name"].lower() == args.field.lower():
            target_field = field
            break
    if not target_field:
        available = [f["name"] for f in fields.get("fields", [])]
        die(ScriptError(
            f"Field '{args.field}' not found in project #{project_number}",
            hint=f"Available fields: {', '.join(available)}",
        ))

    # Step 3: Get item ID by issue/PR number
    items = run_gh(
        "project", "item-list", str(project_number),
        "--owner", owner,
        "--format", "json",
        "--limit", str(DEFAULT_LIMIT),
        json_output=True,
    )
    item_id = None
    for item in items.get("items", []):
        content = item.get("content", {})
        if content.get("number") == args.item:
            item_id = item["id"]
            break
    if not item_id:
        die(ScriptError(
            f"Item #{args.item} not found in project #{project_number}",
            hint="Check the issue/PR number. Draft items have no number.",
        ))

    # Step 4: Build edit command based on field type
    edit_args = [
        "project", "item-edit",
        "--id", item_id,
        "--project-id", project_id,
        "--field-id", target_field["id"],
    ]

    field_type = target_field.get("type", "").upper()
    if field_type == "SINGLE_SELECT":
        option_id = None
        for opt in target_field.get("options", []):
            if opt["name"].lower() == args.value.lower():
                option_id = opt["id"]
                break
        if not option_id:
            available = [o["name"] for o in target_field.get("options", [])]
            die(ScriptError(
                f"Option '{args.value}' not found for field '{args.field}'",
                hint=f"Available options: {', '.join(available)}",
            ))
        edit_args.extend(["--single-select-option-id", option_id])
    elif field_type == "TEXT":
        edit_args.extend(["--text", args.value])
    elif field_type == "NUMBER":
        edit_args.extend(["--number", args.value])
    elif field_type == "DATE":
        edit_args.extend(["--date", args.value])
    elif field_type == "ITERATION":
        edit_args.extend(["--iteration-id", args.value])
    else:
        die(ScriptError(
            f"Unsupported field type '{field_type}' for field '{args.field}'",
            hint="Supported types: SINGLE_SELECT, TEXT, NUMBER, DATE, ITERATION",
        ))

    run_gh(*edit_args)
    print_success(f"Set {args.field}='{args.value}' on item #{args.item}")


def cmd_list(args: argparse.Namespace) -> None:
    """List projects for an owner."""
    result = run_gh(
        "project", "list",
        "--owner", args.owner,
        "--format", "json",
        json_output=True,
    )
    projects = result.get("projects", [])
    if args.json:
        print_json(projects)
    else:
        rows = [
            {"number": p["number"], "title": p["title"], "url": p.get("url", "")}
            for p in projects
        ]
        print_table(rows, ["number", "title", "url"])


def cmd_add(args: argparse.Namespace) -> None:
    """Add an issue or PR to a project by URL."""
    run_gh(
        "project", "item-add", str(args.project),
        "--owner", args.owner,
        "--url", args.url,
    )
    print_success(f"Added {args.url} to project #{args.project}")


def _get_field_value(item: dict, field_name: str) -> str:
    """Extract a field value from a project item by field name."""
    for key, val in item.items():
        if key.lower() == field_name.lower() and isinstance(val, str):
            return val
    return "(none)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GitHub Projects v2 operations",
        prog="gh_project.py",
    )
    parser.add_argument("--owner", default="@me", help="Project owner (default: @me)")
    sub = parser.add_subparsers(dest="action", required=True)

    # status
    p_status = sub.add_parser("status", help="Show project board status")
    p_status.add_argument("project", type=int, help="Project number")
    p_status.add_argument("--group-by", default="Status", help="Field to group by (default: Status)")
    p_status.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Max items to fetch")
    p_status.add_argument("--json", action="store_true", help="Output as JSON")

    # edit-field
    p_edit = sub.add_parser("edit-field", help="Edit item field by human-readable names")
    p_edit.add_argument("project", type=int, help="Project number")
    p_edit.add_argument("--item", type=int, required=True, help="Issue/PR number")
    p_edit.add_argument("--field", required=True, help="Field name (e.g., Status)")
    p_edit.add_argument("--value", required=True, help="Field value (e.g., In Progress)")

    # list
    p_list = sub.add_parser("list", help="List projects")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")

    # add
    p_add = sub.add_parser("add", help="Add issue/PR to project")
    p_add.add_argument("project", type=int, help="Project number")
    p_add.add_argument("--url", required=True, help="Issue or PR URL")

    args = parser.parse_args()
    actions = {"status": cmd_status, "edit-field": cmd_edit_field, "list": cmd_list, "add": cmd_add}
    try:
        actions[args.action](args)
    except ScriptError as exc:
        die(exc)


if __name__ == "__main__":
    main()
