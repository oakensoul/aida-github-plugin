#!/usr/bin/env python3
"""Structured queries for PRs, issues, and workflow runs.

Provides clean JSON or table output without jq fumbling.
"""

from __future__ import annotations

import argparse

from utils.cli import run_gh
from utils.errors import ScriptError, die
from utils.output import print_json, print_table

# Standard --json fields for each resource type
PR_FIELDS = "number,title,state,author,labels,headRefName,url,isDraft,reviewDecision,statusCheckRollup"
ISSUE_FIELDS = "number,title,state,labels,assignees,milestone,url,createdAt"
RUN_FIELDS = "databaseId,displayTitle,status,conclusion,event,headBranch,url,createdAt"


def cmd_prs(args: argparse.Namespace) -> None:
    """List pull requests with structured output."""
    gh_args = ["pr", "list", "--json", PR_FIELDS, "--limit", str(args.limit)]
    if args.state:
        gh_args.extend(["--state", args.state])
    if args.label:
        gh_args.extend(["--label", args.label])
    if args.author:
        gh_args.extend(["--author", args.author])
    if args.base:
        gh_args.extend(["--base", args.base])
    if args.search:
        gh_args.extend(["--search", args.search])

    prs = run_gh(*gh_args, json_output=True)
    if args.json:
        print_json(prs)
    else:
        rows = []
        for pr in prs:
            labels = ",".join(lb["name"] for lb in pr.get("labels", []))
            rows.append({
                "number": f"#{pr['number']}",
                "title": _truncate(pr["title"], 50),
                "state": pr["state"],
                "author": pr.get("author", {}).get("login", ""),
                "labels": labels,
            })
        print_table(rows, ["number", "title", "state", "author", "labels"])


def cmd_issues(args: argparse.Namespace) -> None:
    """List issues with structured output."""
    gh_args = ["issue", "list", "--json", ISSUE_FIELDS, "--limit", str(args.limit)]
    if args.state:
        gh_args.extend(["--state", args.state])
    if args.label:
        gh_args.extend(["--label", args.label])
    if args.assignee:
        gh_args.extend(["--assignee", args.assignee])
    if args.milestone:
        gh_args.extend(["--milestone", args.milestone])
    if args.search:
        gh_args.extend(["--search", args.search])

    issues = run_gh(*gh_args, json_output=True)
    if args.json:
        print_json(issues)
    else:
        rows = []
        for issue in issues:
            labels = ",".join(lb["name"] for lb in issue.get("labels", []))
            milestone = (issue.get("milestone") or {}).get("title", "")
            rows.append({
                "number": f"#{issue['number']}",
                "title": _truncate(issue["title"], 50),
                "state": issue["state"],
                "labels": labels,
                "milestone": milestone,
            })
        print_table(rows, ["number", "title", "state", "labels", "milestone"])


def cmd_runs(args: argparse.Namespace) -> None:
    """List workflow runs with structured output."""
    gh_args = ["run", "list", "--json", RUN_FIELDS, "--limit", str(args.limit)]
    if args.branch:
        gh_args.extend(["--branch", args.branch])
    if args.status:
        gh_args.extend(["--status", args.status])
    if args.workflow:
        gh_args.extend(["--workflow", args.workflow])

    runs = run_gh(*gh_args, json_output=True)
    if args.json:
        print_json(runs)
    else:
        rows = []
        for run in runs:
            rows.append({
                "id": run["databaseId"],
                "title": _truncate(run["displayTitle"], 40),
                "status": run["status"],
                "conclusion": run.get("conclusion") or "",
                "branch": run.get("headBranch", ""),
                "event": run.get("event", ""),
            })
        print_table(rows, ["id", "title", "status", "conclusion", "branch", "event"])


def cmd_checks(args: argparse.Namespace) -> None:
    """Show status checks for a PR."""
    pr_data = run_gh(
        "pr", "view", str(args.pr),
        "--json", "statusCheckRollup,title,number",
        json_output=True,
    )
    checks = pr_data.get("statusCheckRollup", [])
    if args.json:
        print_json({"pr": pr_data.get("number"), "checks": checks})
    else:
        rows = []
        for check in checks:
            rows.append({
                "name": check.get("name", check.get("context", "")),
                "status": check.get("status", ""),
                "conclusion": check.get("conclusion", ""),
            })
        print_table(rows, ["name", "status", "conclusion"])


def _truncate(text: str, length: int) -> str:
    """Truncate text with ellipsis if longer than length."""
    if len(text) <= length:
        return text
    return text[: length - 1] + "…"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Structured queries for GitHub resources",
        prog="gh_query.py",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # prs
    p_prs = sub.add_parser("prs", help="List pull requests")
    p_prs.add_argument("--state", choices=["open", "closed", "merged", "all"])
    p_prs.add_argument("--label", help="Filter by label")
    p_prs.add_argument("--author", help="Filter by author")
    p_prs.add_argument("--base", help="Filter by base branch")
    p_prs.add_argument("--search", help="Search query")
    p_prs.add_argument("--limit", type=int, default=30)
    p_prs.add_argument("--json", action="store_true", help="Output as JSON")

    # issues
    p_issues = sub.add_parser("issues", help="List issues")
    p_issues.add_argument("--state", choices=["open", "closed", "all"])
    p_issues.add_argument("--label", help="Filter by label")
    p_issues.add_argument("--assignee", help="Filter by assignee")
    p_issues.add_argument("--milestone", help="Filter by milestone title")
    p_issues.add_argument("--search", help="Search query")
    p_issues.add_argument("--limit", type=int, default=30)
    p_issues.add_argument("--json", action="store_true", help="Output as JSON")

    # runs
    p_runs = sub.add_parser("runs", help="List workflow runs")
    p_runs.add_argument("--branch", help="Filter by branch")
    p_runs.add_argument("--status", help="Filter by status")
    p_runs.add_argument("--workflow", help="Filter by workflow name or file")
    p_runs.add_argument("--limit", type=int, default=20)
    p_runs.add_argument("--json", action="store_true", help="Output as JSON")

    # checks
    p_checks = sub.add_parser("checks", help="Show PR status checks")
    p_checks.add_argument("pr", type=int, help="PR number")
    p_checks.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    actions = {"prs": cmd_prs, "issues": cmd_issues, "runs": cmd_runs, "checks": cmd_checks}
    try:
        actions[args.action](args)
    except ScriptError as exc:
        die(exc)


if __name__ == "__main__":
    main()
