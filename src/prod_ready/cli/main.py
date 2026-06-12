"""CLI entry point for prod-ready."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from prod_ready import __version__
from prod_ready.core.engine import assess
from prod_ready.core.rubric import list_app_types, load_rubric
from prod_ready.core.models import Severity

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="prod-ready")
def main():
    """prod-ready — Dynamic production-readiness assessment framework.

    This is an assessment tool, not a certification engine.
    It surfaces gaps and recommends fixes — the decisions are yours.
    """
    pass


@main.command()
@click.option(
    "--type", "app_type", required=True,
    help="Application type to assess (e.g. web-api, data-pipeline).",
)
@click.option(
    "--path", "project_path", default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the project root.",
)
@click.option(
    "--format", "output_format", default="table",
    type=click.Choice(["table", "json", "yaml"], case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--rubric-version", default=None,
    help="Rubric version to use (default: latest).",
)
@click.option(
    "--exclude", multiple=True,
    help="Check IDs to exclude (repeatable).",
)
def assess_cmd(app_type: str, project_path: Path, output_format: str,
               rubric_version: str | None, exclude: tuple[str, ...]):
    """Run a production-readiness assessment."""
    config = {"exclude_checks": list(exclude)} if exclude else {}

    try:
        result = assess(
            app_type=app_type,
            project_path=str(project_path),
            rubric_version=rubric_version,
            config=config,
        )
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(f"[dim]Available types: {', '.join(list_app_types())}[/dim]")
        sys.exit(1)

    if output_format == "json":
        console.print(json.dumps(_result_to_dict(result), indent=2))
    elif output_format == "yaml":
        import yaml
        console.print(yaml.dump(_result_to_dict(result), default_flow_style=False))
    else:
        _print_table(result)


@main.command("list-types")
def list_types():
    """List available app types."""
    types = list_app_types()
    if not types:
        console.print("[yellow]No app types configured.[/yellow]")
        return
    console.print("[bold]Available app types:[/bold]")
    for t in types:
        normalized = t.replace("-", "_")
        try:
            rubric = load_rubric(normalized)
            name = rubric.get("app_type", t)
            ver = rubric.get("_resolved_version", "?")
            reviewed = rubric.get("last_reviewed", "?")
            console.print(f"  [cyan]{t}[/cyan] — {name} (v{ver}, reviewed {reviewed})")
        except Exception:
            console.print(f"  [cyan]{t}[/cyan]")


@main.command()
@click.option(
    "--type", "app_type", required=True,
    help="Application type.",
)
def info(app_type: str):
    """Show rubric info for an app type."""
    try:
        rubric = load_rubric(app_type)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    console.print(f"[bold]App Type:[/bold] {rubric.get('app_type', app_type)}")
    console.print(f"[bold]Version:[/bold] {rubric.get('_resolved_version', '?')}")
    console.print(f"[bold]Last Reviewed:[/bold] {rubric.get('last_reviewed', '?')}")

    from prod_ready.core.rubric import get_categories
    cats = get_categories(rubric)
    console.print(f"\n[bold]Categories ({len(cats)}):[/bold]")
    for cat in cats:
        checks = rubric[cat].get("checks", []) if isinstance(rubric[cat], dict) else []
        console.print(f"  [cyan]{cat}[/cyan] — {len(checks)} checks")


def _print_table(result):
    """Render assessment result as a rich table."""
    severity_color = {
        Severity.PASS: "green",
        Severity.WARN: "yellow",
        Severity.FAIL: "red",
    }
    severity_icon = {
        Severity.PASS: "✅",
        Severity.WARN: "⚠️",
        Severity.FAIL: "❌",
    }

    color = severity_color[result.severity]
    icon = severity_icon[result.severity]

    console.print(
        f"\n[bold]prod-ready Assessment — {result.app_type}[/bold]"
    )
    console.print("─" * 40)
    console.print(
        f"Overall Score: [{color}]{result.overall_score}/100  {icon}  "
        f"{result.severity.value.upper()}[/{color}]"
    )
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    for cat in result.categories:
        c_color = severity_color[cat.severity]
        c_icon = severity_icon[cat.severity]
        table.add_row(
            cat.category.value,
            f"{cat.score:.0f}/{cat.max_score:.0f}",
            f"[{c_color}]{c_icon} {cat.severity.value}[/{c_color}]",
        )

    console.print(table)
    console.print()
    console.print(
        f"Gaps Found: {result.total_gaps}  |  "
        f"Critical: {result.critical_gaps}  |  "
        f"High: {result.high_gaps}"
    )
    console.print()
    console.print("[dim]This is an assessment, not a certification.[/dim]")


def _result_to_dict(result) -> dict:
    """Convert AssessmentResult to a plain dict for serialization."""
    return {
        "app_type": result.app_type,
        "project_path": result.project_path,
        "overall_score": result.overall_score,
        "severity": result.severity.value,
        "rubric_version": result.rubric_version,
        "timestamp": result.timestamp,
        "total_gaps": result.total_gaps,
        "critical_gaps": result.critical_gaps,
        "high_gaps": result.high_gaps,
        "categories": [
            {
                "category": cat.category.value,
                "score": cat.score,
                "max_score": cat.max_score,
                "severity": cat.severity.value,
                "checks": [
                    {
                        "id": c.check_id,
                        "name": c.name,
                        "severity": c.severity.value,
                        "score": c.score,
                        "message": c.message,
                        "remediation": c.remediation,
                    }
                    for c in cat.checks
                ],
            }
            for cat in result.categories
        ],
        "metadata": result.metadata,
    }


if __name__ == "__main__":
    main()
