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
from .card import generate_card
from .viral import offer_share
from . import telemetry
from . import success

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

            console.print("\n[green]Profile analyzed successfully[/green]")
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
@click.option("--no-card", is_flag=True, help="Skip generating shareable card")
def find(lang, min_stars, max_age, limit, no_card):
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

            # Log telemetry
            telemetry.log_event("search", {
                "languages": languages,
                "results_count": len(scored_issues),
                "top_score": scored_issues[0][0].total_score if scored_issues else 0,
            }, config.get("username"))

            # Show live stats
            telemetry.display_stats(console)

            # Generate shareable card
            if not no_card and scored_issues:
                try:
                    card_path = generate_card(scored_issues[:limit], config["username"])
                    console.print(f"\n[dim]Card saved: {card_path}[/dim]")
                except Exception as e:
                    # Don't fail if card generation fails
                    pass

                # Offer viral sharing
                offer_share(scored_issues[:limit], console)

        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            import traceback
            traceback.print_exc()


@cli.command()
def stats():
    """Show live activity stats."""
    if not telemetry.is_enabled():
        console.print("[yellow]Telemetry is disabled.[/yellow]")
        console.print("\nEnable it to see live stats and help improve the tool:")
        console.print("  gfi telemetry --enable")
        return

    telemetry.display_stats(console)


@cli.command()
@click.option("--enable", is_flag=True, help="Enable anonymous telemetry")
@click.option("--disable", is_flag=True, help="Disable telemetry")
def telemetry_cmd(enable, disable):
    """Manage telemetry settings."""

    if enable:
        telemetry.enable_telemetry()
        console.print("[green]Telemetry enabled[/green]")
        console.print("\nWe collect anonymous usage data to show live activity stats.")
        console.print("No personal information is collected. You can disable anytime with:")
        console.print("  gfi telemetry --disable")
    elif disable:
        telemetry.disable_telemetry()
        console.print("[yellow]Telemetry disabled[/yellow]")
    else:
        status = "enabled" if telemetry.is_enabled() else "disabled"
        console.print(f"Telemetry is currently [cyan]{status}[/cyan]")
        console.print(f"\nRun 'gfi telemetry --{'disable' if telemetry.is_enabled() else 'enable'}' to change")


# Register telemetry command
cli.add_command(telemetry_cmd, name="telemetry")


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


@cli.command()
@click.option("--lang", multiple=True, help="Filter by language (can use multiple times)")
@click.option("--min-stars", type=int, default=50, help="Minimum repo stars")
def lucky(lang, min_stars):
    """Find ONE perfect issue - feeling lucky mode."""

    if not CONFIG_PATH.exists():
        console.print("[red]Error:[/red] Not initialized. Run 'gfi init' first.")
        return

    config = json.loads(CONFIG_PATH.read_text())
    languages = list(lang) if lang else config.get("languages", [])[:3]

    with console.status("[cyan]Finding your perfect match..."):
        try:
            client = GitHubClient(config["token"])
            scorer = IssueScorer(client)

            # Get more candidates for better lucky pick
            issues = client.search_good_first_issues(
                languages=languages,
                min_stars=min_stars,
                max_age_days=30,
                limit=50
            )

            # Score with lucky algorithm
            lucky_issues = []
            for issue in issues[:30]:  # Score subset
                score = scorer.score_for_lucky(issue)
                if score.lucky_score and score.lucky_score > 0.4:
                    lucky_issues.append((score, issue))

            if not lucky_issues:
                console.print("[yellow]No lucky match found. Try broadening your search.[/yellow]")
                return

            # Sort by lucky score and take the best
            lucky_issues.sort(key=lambda x: x[0].lucky_score, reverse=True)
            best_score, best_issue = lucky_issues[0]

            # Display the ONE perfect match
            console.print("\n[bold green]Your Perfect Match[/bold green]\n")
            display_issue_detail(best_issue, best_score, console)

            # Offer to generate card
            try:
                card_path = generate_card([(best_score, best_issue)], config["username"])
                console.print(f"\n[dim]Card saved: {card_path}[/dim]")
            except:
                pass

        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.argument("issue_url")
@click.option("--pr", help="URL of your pull request")
@click.option("--notes", default="", help="Optional notes about the contribution")
def success_cmd(issue_url, pr, notes):
    """Report a successful contribution."""

    success.report_success(issue_url, pr, notes)

    console.print("[green]Success reported![/green]")
    console.print(f"\nIssue: {issue_url}")
    if pr:
        console.print(f"PR: {pr}")

    # Log telemetry
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
        telemetry.log_event("success", {
            "issue_url": issue_url,
            "has_pr": bool(pr),
        }, config.get("username"))

    console.print("\nThanks for contributing to open source!")
    console.print("Share your achievement on Twitter to inspire others.")


# Register success command
cli.add_command(success_cmd, name="success")


@cli.command()
def wins():
    """Show your successful contributions."""
    success.display_successes(console)


if __name__ == "__main__":
    cli()
