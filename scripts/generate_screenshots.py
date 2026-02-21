"""Generate screenshots for README using Rich SVG export."""

import sys
import os
from pathlib import Path
from rich.console import Console

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gfi.github import GitHubClient
from gfi.analyzer import ProfileAnalyzer
from gfi.scorer import IssueScorer
from gfi.display import display_issues, display_issue_detail
from rich.panel import Panel
import json

# Load config
CONFIG_PATH = Path.home() / ".gfi-config.json"
config = json.loads(CONFIG_PATH.read_text())

# Create output directory
screenshots_dir = Path(__file__).parent.parent / "docs" / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)

# 1. Screenshot: gfi find output
print("Generating screenshot 1: gfi find output...")
console = Console(record=True, width=100)

client = GitHubClient(config["token"])
analyzer = ProfileAnalyzer(client)
profile = analyzer.build_profile()
scorer = IssueScorer(profile)

console.print("\n[bold cyan]Good First Issue Finder[/bold cyan]\n")
console.print(f"Searching for issues matching your profile...")
console.print(f"Languages: {', '.join(profile.languages[:3])}\n")

# Get some issues
issues = client.search_good_first_issues(
    languages=profile.languages[:3],
    min_stars=10,
    max_age_days=30,
    limit=5
)

scored = [(scorer.score_issue(issue), issue) for issue in issues]
scored.sort(key=lambda x: x[0].total_score, reverse=True)

display_issues(scored[:5], console)

console.print(f"\n[dim]Showing top {len(scored[:5])} issues[/dim]")
console.print("[dim]Run 'gfi show <url>' for details[/dim]\n")

console.save_svg(str(screenshots_dir / "demo-cli.svg"), title="Good First Issue Finder")
console.save_text(str(screenshots_dir / "demo-cli.txt"))
print(f"✓ Saved demo-cli.svg and demo-cli.txt")

# 2. Screenshot: gfi init success
print("\nGenerating screenshot 2: gfi init success...")
console2 = Console(record=True, width=100)

console2.print("\n[cyan]Analyzing your GitHub profile...[/cyan]")
console2.print("\n[green]✓ Profile analyzed successfully[/green]")
console2.print(f"\nUsername: [cyan]{profile.username}[/cyan]")
console2.print(f"Top languages: {', '.join(profile.languages[:5])}")
console2.print(f"Starred repos: {profile.starred_count}")
console2.print(f"Interests: {', '.join(profile.topics[:5])}")
console2.print("\n[green]Configuration saved to ~/.gfi-config.json[/green]\n")

console2.save_svg(str(screenshots_dir / "demo-init.svg"), title="GFI Init")
console2.save_text(str(screenshots_dir / "demo-init.txt"))
print(f"✓ Saved demo-init.svg and demo-init.txt")

# 3. Screenshot: gfi show detail view
if scored:
    print("\nGenerating screenshot 3: gfi show detail...")
    console3 = Console(record=True, width=100)

    top_score, top_issue = scored[0]
    display_issue_detail(top_issue, top_score, console3)

    console3.save_svg(str(screenshots_dir / "demo-show.svg"), title="Issue Detail")
    console3.save_text(str(screenshots_dir / "demo-show.txt"))
    print(f"✓ Saved demo-show.svg and demo-show.txt")

print(f"\n✓ All screenshots saved to {screenshots_dir}")
print("\nNext steps:")
print("1. Convert SVG to PNG using online tool or ImageMagick")
print("2. Update README.md to reference images")
print("3. Commit and push")
