#!/usr/bin/env python3
"""Template-based PR and issue body generation via Jinja2.

Renders markdown templates with context variables (branch, issue number,
author, etc.) for consistent, well-structured PR and issue bodies.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from jinja2.sandbox import SandboxedEnvironment
from utils.cli import get_repo_context, run_gh, run_git
from utils.errors import ScriptError, die

TEMPLATES_DIR = Path(__file__).parent / "templates"


def cmd_render(args: argparse.Namespace) -> None:
    """Render a template with context variables."""
    template_dir = Path(args.template_dir) if args.template_dir else TEMPLATES_DIR
    if not template_dir.exists():
        die(ScriptError(
            f"Template directory not found: {template_dir}",
            hint="Provide --template-dir or create scripts/templates/",
        ))

    env = SandboxedEnvironment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    try:
        template = env.get_template(args.template)
    except TemplateNotFound:
        available = [p.name for p in template_dir.glob("*.j2")]
        die(ScriptError(
            f"Template '{args.template}' not found",
            hint=f"Available templates: {', '.join(available) or '(none)'}",
        ))

    context = _build_context(args)
    rendered = template.render(**context)
    print(rendered)


def cmd_list(args: argparse.Namespace) -> None:
    """List available templates."""
    template_dir = Path(args.template_dir) if args.template_dir else TEMPLATES_DIR
    if not template_dir.exists():
        print("(no templates directory)")
        return

    templates = sorted(template_dir.glob("*.j2"))
    if not templates:
        print("(no templates found)")
        return

    for t in templates:
        print(t.name)


def _build_context(args: argparse.Namespace) -> dict:
    """Build template context from args and git/gh state."""
    context: dict = {}

    # Parse --var key=value pairs
    if args.var:
        for pair in args.var:
            if "=" not in pair:
                die(ScriptError(f"Invalid --var format: '{pair}'", hint="Use --var key=value"))
            key, value = pair.split("=", 1)
            context[key] = value

    # Auto-detect context from git/gh if not provided
    if "branch" not in context:
        try:
            result = run_git("rev-parse", "--abbrev-ref", "HEAD")
            context["branch"] = result.stdout.strip()
        except ScriptError:
            pass

    if "repo" not in context or "owner" not in context:
        try:
            repo_ctx = get_repo_context()
            context.setdefault("owner", repo_ctx["owner"])
            context.setdefault("repo", repo_ctx["repo"])
        except ScriptError:
            pass

    if "author" not in context:
        try:
            result = run_gh("api", "user", json_output=True)
            context["author"] = result.get("login", "")
        except ScriptError:
            pass

    return context


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Template-based PR/issue body generation",
        prog="gh_pr_body.py",
    )
    parser.add_argument("--template-dir", help="Path to templates directory")
    sub = parser.add_subparsers(dest="action", required=True)

    # render
    p_render = sub.add_parser("render", help="Render a template")
    p_render.add_argument("template", help="Template filename (e.g., pr_default.md.j2)")
    p_render.add_argument("--var", action="append", help="Template variable as key=value (repeatable)")

    # list
    sub.add_parser("list", help="List available templates")

    args = parser.parse_args()
    actions = {"render": cmd_render, "list": cmd_list}
    try:
        actions[args.action](args)
    except ScriptError as exc:
        die(exc)


if __name__ == "__main__":
    main()
