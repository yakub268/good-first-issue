"""Viral loop utilities - sharing and social features."""

import webbrowser
import urllib.parse
from typing import List, Tuple
from .github import Issue
from .scorer import IssueScore


def generate_tweet_text(issue: Issue, score: IssueScore) -> str:
    """Generate pre-filled tweet text for an issue match."""

    # Clean, natural tweet (not promotional)
    tweet_parts = [
        f"Just found a {score.total_score:.2f}-scored issue in {issue.repo_owner}/{issue.repo_name}",
        f'"{issue.title[:80]}"',
    ]

    # Add context based on score factors
    if score.clarity_score > 0.7:
        tweet_parts.append("Clear description, responsive maintainers.")

    # Add call to action
    tweet_parts.append("Found it using Good First Issue Finder")
    tweet_parts.append("github.com/yakub268/good-first-issue")

    return "\n\n".join(tweet_parts)


def offer_share(scored_issues: List[Tuple[IssueScore, Issue]], console) -> bool:
    """Offer to share results on Twitter."""

    if not scored_issues:
        return False

    console.print("\n[dim]Tip: Sharing your match helps other developers discover this tool[/dim]")
    console.print("[dim]Press 's' to compose a tweet, or any other key to skip[/dim]", end="")

    try:
        import sys
        import tty
        import termios

        # Get single keypress (Unix/Mac)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except:
        # Fallback for Windows or if tty fails
        console.print("")
        response = input().strip().lower()
        ch = response[0] if response else 'n'

    console.print("")  # Newline after keypress

    if ch.lower() == 's':
        open_twitter_compose(scored_issues[0], console)
        return True

    return False


def open_twitter_compose(scored_issue: Tuple[IssueScore, Issue], console):
    """Open browser with pre-filled tweet."""

    score, issue = scored_issue
    tweet_text = generate_tweet_text(issue, score)

    # URL encode the tweet
    encoded_text = urllib.parse.quote(tweet_text)
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"

    try:
        webbrowser.open(twitter_url)
        console.print("[green]Opened Twitter in your browser[/green]")
    except Exception as e:
        console.print(f"[yellow]Couldn't open browser. Copy this link:[/yellow]\n{twitter_url}")
