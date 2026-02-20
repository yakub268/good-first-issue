"""CLI interface for Good First Issue Finder."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from pathlib import Path
import json
import os
from dotenv import load_dotenv

from .github import GitHubClient
from .analyzer import ProfileAnalyzer
from .scorer import IssueScorer
from .display import display_issues, display_issue_detail

console = Console()
load_dotenv()

CONFIG_PATH = Path.home() / ".gfi-config.json"


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Find good first issues in projects you actually care about."""
    pass


@cli.command()
@click.option("--token", help="GitHub personal access token (or set GITHUB_TOKEN env var)")
def init(token):
    """Initialize GFI with your GitHub profile."""

    if not token:
        token = os.getenv("GITHUB_TOKEN")

    if not token:
        console.print("[red]Error:[/red] GitHub token required")
        console.print("\nCreate a token at: https://github.com/settings/tokens")
        console.print("Required scopes: public_repo, read:user")
        console.print("\nThen run: gfi init --token YOUR_TOKEN")
        console.print("Or set GITHUB_TOKEN environment variable")
        return

    with console.status("[cyan]Analyzing your GitHub profile..."):
        try:
            client = GitHubClient(token)
            analyzer = ProfileAnalyzer(client)
            profile = analyzer.build_profile()

            # Save config
            config = {
                "token": token,
                "username": profile.username,
                "languages": profile.languages,
                "interests": profile.topics,
            }
            CONFIG_PATH.write_text(json.dumps(config, indent=2))

            console.print("\n[green]✓[/green] Profile analyzed successfully!")
            console.print(f"\nUsername: [cyan]{profile.username}[/cyan]")
            console.print(f"Top languages: {', '.join(profile.languages[:5])}")
            console.print(f"Starred repos: {profile.starred_count}")
            console.print(f"Contributed to: {profile.contributed_count} projects")

        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            return


@cli.command()
@click.option("--lang", multiple=True, help="Filter by language (can use multiple times)")
@click.option("--min-stars", type=int, default=50, help="Minimum repo stars")
@click.option("--max-age", type=int, default=30, help="Maximum issue age in days")
@click.option("--limit", type=int, default=10, help="Number of issues to show")
def find(lang, min_stars, max_age, limit):
    """Find good first issues matching your profile."""

    if not CONFIG_PATH.exists():
        console.print("[red]Error:[/red] Not initialized. Run 'gfi init' first.")
        return

    config = json.loads(CONFIG_PATH.read_text())

    # Use specified languages or fall back to profile languages
    languages = list(lang) if lang else config.get("languages", [])[:3]

    with console.status(f"[cyan]Searching for issues in {', '.join(languages)}..."):
        try:
            client = GitHubClient(config["token"])
            scorer = IssueScorer(client)

            # Search for issues
            issues = client.search_good_first_issues(
                languages=languages,
                min_stars=min_stars,
                max_age_days=max_age,
                limit=limit * 3  # Get more to filter
            )

            # Score and rank
            scored_issues = []
            for issue in issues[:limit * 2]:  # Score subset for speed
                score = scorer.score_issue(issue)
                if score.total_score > 0.3:  # Minimum threshold
                    scored_issues.append((score, issue))

            # Sort by score
            scored_issues.sort(key=lambda x: x[0].total_score, reverse=True)

            # Display top results
            display_issues(scored_issues[:limit], console)

        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            import traceback
            traceback.print_exc()


@cli.command()
@click.argument("issue_url")
def show(issue_url):
    """Show detailed information about a specific issue."""

    if not CONFIG_PATH.exists():
        console.print("[red]Error:[/red] Not initialized. Run 'gfi init' first.")
        return

    config = json.loads(CONFIG_PATH.read_text())

    try:
        # Parse URL to get owner/repo/issue_number
        parts = issue_url.rstrip("/").split("/")
        if len(parts) < 2:
            console.print("[red]Error:[/red] Invalid GitHub issue URL")
            return

        issue_number = int(parts[-1])
        repo_name = parts[-3]
        owner = parts[-4]

        client = GitHubClient(config["token"])
        issue = client.get_issue(owner, repo_name, issue_number)
        scorer = IssueScorer(client)
        score = scorer.score_issue(issue)

        display_issue_detail(issue, score, console)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


if __name__ == "__main__":
    cli()
