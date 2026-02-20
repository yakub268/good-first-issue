"""Success story tracking."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


SUCCESS_FILE = Path.home() / ".gfi-successes.json"


def load_successes() -> list:
    """Load success stories from local file."""
    if not SUCCESS_FILE.exists():
        return []

    try:
        return json.loads(SUCCESS_FILE.read_text())
    except:
        return []


def save_successes(successes: list):
    """Save success stories to local file."""
    SUCCESS_FILE.write_text(json.dumps(successes, indent=2))


def report_success(issue_url: str, pr_url: Optional[str] = None, notes: str = ""):
    """Report a successful contribution."""

    successes = load_successes()

    success = {
        "issue_url": issue_url,
        "pr_url": pr_url,
        "notes": notes,
        "reported_at": datetime.utcnow().isoformat(),
    }

    successes.append(success)
    save_successes(successes)

    return success


def get_success_count() -> int:
    """Get count of successful contributions."""
    return len(load_successes())


def display_successes(console):
    """Display user's success stories."""

    successes = load_successes()

    if not successes:
        console.print("[yellow]No successes reported yet.[/yellow]")
        console.print("\nAfter you submit a PR, report it with:")
        console.print("  gfi success <issue-url> --pr <pr-url>")
        return

    console.print(f"[green]You've completed {len(successes)} contributions![/green]\n")

    for i, success in enumerate(successes[-10:], 1):  # Show last 10
        console.print(f"{i}. {success['issue_url']}")
        if success.get('pr_url'):
            console.print(f"   PR: {success['pr_url']}")
        if success.get('notes'):
            console.print(f"   Note: {success['notes']}")
        console.print(f"   Completed: {success['reported_at'][:10]}\n")
