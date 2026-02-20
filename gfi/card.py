"""Generate shareable result cards."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Tuple
from .github import Issue
from .scorer import IssueScore
import tempfile


def generate_card(scored_issues: List[Tuple[IssueScore, Issue]], username: str) -> Path:
    """Generate a shareable PNG card with results."""

    # Card dimensions
    width = 1200
    height = 630  # Twitter/LinkedIn optimal size

    # Colors (clean, professional)
    bg_color = (15, 23, 42)  # Dark slate
    card_bg = (30, 41, 59)  # Slate 800
    text_color = (248, 250, 252)  # Slate 50
    accent_color = (99, 102, 241)  # Indigo 500
    secondary_color = (148, 163, 184)  # Slate 400

    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to use system fonts, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        heading_font = ImageFont.truetype("arial.ttf", 32)
        body_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw main card background
    draw.rounded_rectangle([(40, 40), (width-40, height-40)], radius=20, fill=card_bg)

    # Title
    draw.text((80, 80), "Good First Issue Finder", fill=accent_color, font=heading_font)

    # Results count
    if scored_issues:
        top_score = scored_issues[0][0]
        top_issue = scored_issues[0][1]

        # Main result
        result_text = f"Found {len(scored_issues)} matches"
        draw.text((80, 140), result_text, fill=text_color, font=body_font)

        # Top match
        draw.text((80, 200), "Top Match:", fill=secondary_color, font=small_font)

        # Issue title (truncated)
        issue_title = top_issue.title
        if len(issue_title) > 60:
            issue_title = issue_title[:57] + "..."
        draw.text((80, 240), issue_title, fill=text_color, font=body_font)

        # Repo and score
        repo_text = f"{top_issue.repo_owner}/{top_issue.repo_name}"
        score_text = f"Score: {top_score.total_score:.2f}"
        draw.text((80, 290), repo_text, fill=accent_color, font=small_font)
        draw.text((80, 325), score_text, fill=secondary_color, font=small_font)

        # Stats bar
        y_offset = 400
        draw.text((80, y_offset), f"Language: {top_issue.repo_language or 'N/A'}",
                 fill=secondary_color, font=small_font)
        draw.text((400, y_offset), f"Stars: {_format_stars(top_issue.repo_stars)}",
                 fill=secondary_color, font=small_font)
    else:
        draw.text((80, 140), "No matches found", fill=secondary_color, font=body_font)

    # Footer
    footer_y = height - 100
    draw.text((80, footer_y), "github.com/yakub268/good-first-issue",
             fill=secondary_color, font=small_font)

    # Save to temp file
    temp_file = Path(tempfile.gettempdir()) / f"gfi_results_{username}.png"
    img.save(temp_file, "PNG")

    return temp_file


def _format_stars(stars: int) -> str:
    """Format star count."""
    if stars >= 1000:
        return f"{stars/1000:.1f}k"
    return str(stars)
