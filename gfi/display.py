"""Rich terminal display utilities."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from typing import List, Tuple
from .github import Issue
from .scorer import IssueScore


def display_issues(scored_issues: List[Tuple[IssueScore, Issue]], console: Console):
    """Display ranked issues in a table."""

    if not scored_issues:
        console.print("[yellow]No issues found matching your criteria.[/yellow]")
        console.print("\nTry:")
        console.print("  - Different languages (--lang python --lang javascript)")
        console.print("  - Lower minimum stars (--min-stars 10)")
        console.print("  - Longer time window (--max-age 60)")
        return

    table = Table(
        title="Good First Issues",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Score", justify="right", style="green", no_wrap=True)
    table.add_column("Project", style="cyan", no_wrap=True)
    table.add_column("Issue", style="white")
    table.add_column("Lang", style="yellow", no_wrap=True)
    table.add_column("Stars", justify="right", style="yellow", no_wrap=True)

    for score, issue in scored_issues:
        # Truncate long titles
        title = issue.title
        if len(title) > 47:
            title = title[:44] + "..."

        repo_display = f"{issue.repo_owner}/{issue.repo_name}"
        if len(repo_display) > 22:
            repo_display = repo_display[:19] + "..."

        score_display = f"{score.total_score:.2f}"
        stars_display = _format_number(issue.repo_stars)

        table.add_row(
            score_display,
            repo_display,
            title,
            issue.repo_language or "N/A",
            stars_display,
        )

    console.print(table)
    console.print(f"\n[dim]Showing top {len(scored_issues)} issues[/dim]")
    console.print("[dim]Run 'gfi show <url>' for details[/dim]")


def display_issue_detail(issue: Issue, score: IssueScore, console: Console):
    """Display detailed view of a single issue."""

    # Header
    header = f"[bold cyan]{issue.repo_owner}/{issue.repo_name}[/bold cyan] #{issue.number}"
    console.print(Panel(header, style="cyan"))

    # Title
    console.print(f"\n[bold]{issue.title}[/bold]\n")

    # Score breakdown
    score_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    score_table.add_column("Metric", style="dim")
    score_table.add_column("Score", justify="right")

    score_table.add_row("Overall Score", _score_bar(score.total_score))
    score_table.add_row("Clarity", _score_bar(score.clarity_score))
    score_table.add_row("Maintainer Response", _score_bar(score.maintainer_score))
    score_table.add_row("Freshness", _score_bar(score.freshness_score))
    score_table.add_row("Project Activity", _score_bar(score.activity_score))

    console.print(score_table)
    console.print(f"\n[dim]{score.reason}[/dim]\n")

    # Metadata
    meta_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    meta_table.add_column("Field", style="dim")
    meta_table.add_column("Value")

    meta_table.add_row("Language", issue.repo_language or "N/A")
    meta_table.add_row("Stars", _format_number(issue.repo_stars))
    meta_table.add_row("Comments", str(issue.comments))
    meta_table.add_row("Created", issue.created_at.strftime("%Y-%m-%d"))
    meta_table.add_row("Labels", ", ".join(issue.labels[:5]))

    console.print(meta_table)

    # Description
    if issue.body:
        console.print("\n[bold]Description[/bold]\n")
        # Truncate very long descriptions
        body = issue.body
        if len(body) > 1000:
            body = body[:1000] + "\n\n[... truncated ...]"

        try:
            md = Markdown(body)
            console.print(Panel(md, box=box.ROUNDED))
        except Exception:
            console.print(Panel(body, box=box.ROUNDED))

    # Link
    console.print(f"\n[cyan]{issue.html_url}[/cyan]\n")


def _score_bar(score: float) -> str:
    """Generate a visual bar for a score."""
    filled = int(score * 10)
    bar = "█" * filled + "░" * (10 - filled)

    if score >= 0.7:
        color = "green"
    elif score >= 0.4:
        color = "yellow"
    else:
        color = "red"

    return f"[{color}]{bar}[/{color}] {score:.2f}"


def _format_number(num: int) -> str:
    """Format large numbers with k/M suffix."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return str(num)
