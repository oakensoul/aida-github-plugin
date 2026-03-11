#!/usr/bin/env python3
"""REST API wrapper for operations not covered by gh CLI subcommands.

Primarily milestones (gh milestone doesn't exist) and rulesets.
Uses gh api with correct HTTP methods and endpoints.
"""

from __future__ import annotations

import argparse

from utils.cli import get_repo_context, run_gh
from utils.errors import ScriptError, die
from utils.output import print_json, print_success, print_table


def cmd_milestone_list(args: argparse.Namespace) -> None:
    """List milestones for the current repo."""
    ctx = get_repo_context()
    endpoint = f"repos/{ctx['owner']}/{ctx['repo']}/milestones"
    params = f"?state={args.state}&sort=due_on&direction=asc&per_page=100"
    milestones = run_gh("api", endpoint + params, json_output=True)

    if args.json:
        print_json(milestones)
    else:
        rows = [
            {
                "number": m["number"],
                "title": m["title"],
                "state": m["state"],
                "open": m["open_issues"],
                "closed": m["closed_issues"],
                "due": (m.get("due_on") or "")[:10],
            }
            for m in milestones
        ]
        print_table(rows, ["number", "title", "state", "open", "closed", "due"])


def cmd_milestone_create(args: argparse.Namespace) -> None:
    """Create a milestone."""
    ctx = get_repo_context()
    endpoint = f"repos/{ctx['owner']}/{ctx['repo']}/milestones"
    gh_args = [
        "api", endpoint,
        "--method", "POST",
        "-f", f"title={args.title}",
    ]
    if args.description:
        gh_args.extend(["-f", f"description={args.description}"])
    if args.due_date:
        gh_args.extend(["-f", f"due_on={args.due_date}T00:00:00Z"])

    result = run_gh(*gh_args, json_output=True)
    print_success(f"Created milestone '{args.title}' (#{result['number']})")
    if args.json:
        print_json(result)


def cmd_milestone_close(args: argparse.Namespace) -> None:
    """Close a milestone by number."""
    ctx = get_repo_context()
    endpoint = f"repos/{ctx['owner']}/{ctx['repo']}/milestones/{args.number}"
    run_gh("api", endpoint, "--method", "PATCH", "-f", "state=closed")
    print_success(f"Closed milestone #{args.number}")


def cmd_milestone_edit(args: argparse.Namespace) -> None:
    """Edit a milestone by number."""
    if not any([args.title, args.description, args.due_date, args.state]):
        die(ScriptError(
            "No fields to update",
            hint="Provide at least one of: --title, --description, --due-date, --state",
        ))
    ctx = get_repo_context()
    endpoint = f"repos/{ctx['owner']}/{ctx['repo']}/milestones/{args.number}"
    gh_args = ["api", endpoint, "--method", "PATCH"]
    if args.title:
        gh_args.extend(["-f", f"title={args.title}"])
    if args.description:
        gh_args.extend(["-f", f"description={args.description}"])
    if args.due_date:
        gh_args.extend(["-f", f"due_on={args.due_date}T00:00:00Z"])
    if args.state:
        gh_args.extend(["-f", f"state={args.state}"])

    run_gh(*gh_args, json_output=True)
    print_success(f"Updated milestone #{args.number}")


def cmd_milestone_delete(args: argparse.Namespace) -> None:
    """Delete a milestone by number."""
    ctx = get_repo_context()
    endpoint = f"repos/{ctx['owner']}/{ctx['repo']}/milestones/{args.number}"
    run_gh("api", endpoint, "--method", "DELETE")
    print_success(f"Deleted milestone #{args.number}")


def cmd_rulesets(args: argparse.Namespace) -> None:
    """List repository rulesets."""
    ctx = get_repo_context()
    endpoint = f"repos/{ctx['owner']}/{ctx['repo']}/rulesets"
    rulesets = run_gh("api", endpoint, json_output=True)

    if args.json:
        print_json(rulesets)
    else:
        rows = [
            {
                "id": r["id"],
                "name": r["name"],
                "enforcement": r.get("enforcement", ""),
                "target": r.get("target", ""),
            }
            for r in rulesets
        ]
        print_table(rows, ["id", "name", "enforcement", "target"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="REST API wrapper for milestones and rulesets",
        prog="gh_api.py",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # milestone-list
    p_mlist = sub.add_parser("milestone-list", help="List milestones")
    p_mlist.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p_mlist.add_argument("--json", action="store_true")

    # milestone-create
    p_mcreate = sub.add_parser("milestone-create", help="Create a milestone")
    p_mcreate.add_argument("--title", required=True)
    p_mcreate.add_argument("--description")
    p_mcreate.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    p_mcreate.add_argument("--json", action="store_true")

    # milestone-close
    p_mclose = sub.add_parser("milestone-close", help="Close a milestone")
    p_mclose.add_argument("number", type=int, help="Milestone number")

    # milestone-edit
    p_medit = sub.add_parser("milestone-edit", help="Edit a milestone")
    p_medit.add_argument("number", type=int, help="Milestone number")
    p_medit.add_argument("--title")
    p_medit.add_argument("--description")
    p_medit.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    p_medit.add_argument("--state", choices=["open", "closed"])

    # milestone-delete
    p_mdel = sub.add_parser("milestone-delete", help="Delete a milestone")
    p_mdel.add_argument("number", type=int, help="Milestone number")

    # rulesets
    p_rules = sub.add_parser("rulesets", help="List repository rulesets")
    p_rules.add_argument("--json", action="store_true")

    args = parser.parse_args()
    actions = {
        "milestone-list": cmd_milestone_list,
        "milestone-create": cmd_milestone_create,
        "milestone-close": cmd_milestone_close,
        "milestone-edit": cmd_milestone_edit,
        "milestone-delete": cmd_milestone_delete,
        "rulesets": cmd_rulesets,
    }
    try:
        actions[args.action](args)
    except ScriptError as exc:
        die(exc)


if __name__ == "__main__":
    main()
