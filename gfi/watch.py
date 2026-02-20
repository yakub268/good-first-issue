"""Watch mode daemon for monitoring new good first issues."""

import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple
from .github import GitHubClient, Issue
from .analyzer import ProfileAnalyzer
from .scorer import IssueScorer


WATCH_STATE_FILE = Path.home() / ".gfi-watch-state.json"
CHECK_INTERVAL_HOURS = 6


def load_watch_state() -> dict:
    """Load watch state from file."""
    if not WATCH_STATE_FILE.exists():
        return {
            "last_check": None,
            "seen_issues": [],
            "enabled": False,
        }

    try:
        return json.loads(WATCH_STATE_FILE.read_text())
    except:
        return {"last_check": None, "seen_issues": [], "enabled": False}


def save_watch_state(state: dict):
    """Save watch state to file."""
    WATCH_STATE_FILE.write_text(json.dumps(state, indent=2))


def enable_watch():
    """Enable watch mode."""
    state = load_watch_state()
    state["enabled"] = True
    save_watch_state(state)


def disable_watch():
    """Disable watch mode."""
    state = load_watch_state()
    state["enabled"] = False
    save_watch_state(state)


def is_watch_enabled() -> bool:
    """Check if watch mode is enabled."""
    return load_watch_state().get("enabled", False)


def check_for_new_issues(config: dict) -> List[Tuple[IssueScore, Issue]]:
    """Check for new high-quality issues."""

    client = GitHubClient(config["token"])
    scorer = IssueScorer(client)

    # Search for issues
    languages = config.get("languages", [])[:3]
    issues = client.search_good_first_issues(
        languages=languages,
        min_stars=50,
        max_age_days=7,  # Only recent issues
        limit=20
    )

    # Load state to track seen issues
    state = load_watch_state()
    seen_urls = set(state.get("seen_issues", []))

    # Score and filter new high-quality issues
    new_good_issues = []
    for issue in issues:
        if issue.html_url in seen_urls:
            continue

        score = scorer.score_issue(issue)

        # Only notify for excellent matches (0.7+)
        if score.total_score >= 0.7:
            new_good_issues.append((score, issue))
            seen_urls.add(issue.html_url)

    # Update state
    state["seen_issues"] = list(seen_urls)[-100:]  # Keep last 100
    state["last_check"] = datetime.utcnow().isoformat()
    save_watch_state(state)

    return new_good_issues


def send_notification(title: str, message: str):
    """Send desktop notification."""

    try:
        # Try plyer (cross-platform)
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Good First Issue Finder",
            timeout=10
        )
    except ImportError:
        # Fallback: just print (notification libraries are optional)
        print(f"\n[NOTIFICATION] {title}\n{message}\n")
    except Exception:
        # Silent fail if notifications don't work
        pass


def run_watch_daemon(config: dict):
    """Run watch daemon (checks every 6 hours)."""

    print("Watch mode started. Checking for new issues every 6 hours...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            if not is_watch_enabled():
                print("Watch mode disabled. Exiting...")
                break

            new_issues = check_for_new_issues(config)

            if new_issues:
                # Send notification for best match
                best_score, best_issue = new_issues[0]
                title = f"New Good First Issue ({best_score.total_score:.2f})"
                message = f"{best_issue.title[:80]}\n{best_issue.repo_owner}/{best_issue.repo_name}"

                send_notification(title, message)

                print(f"\nFound {len(new_issues)} new good issues!")
                print(f"Best: {best_issue.title[:60]}... (score: {best_score.total_score:.2f})")
            else:
                print(f"No new good issues found. Next check in {CHECK_INTERVAL_HOURS} hours.")

            # Sleep for 6 hours
            time.sleep(CHECK_INTERVAL_HOURS * 3600)

    except KeyboardInterrupt:
        print("\nWatch mode stopped.")
