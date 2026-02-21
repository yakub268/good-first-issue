"""Tests for card generation."""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
from gfi.card import generate_card, _format_stars
from gfi.github import Issue
from gfi.scorer import IssueScore


def test_generate_card_with_valid_data():
    """Test card generation with valid scored issues."""
    # Create mock issue
    issue = Issue(
        number=42,
        title="Add dark mode support to dashboard",
        url="https://api.github.com/repos/test/repo/issues/42",
        html_url="https://github.com/test/repo/issues/42",
        body="We need dark mode for better UX",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue", "enhancement"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=1500,
        repo_language="Python",
        repo_description="Test repository",
        comments=3,
        author="testuser",
    )

    # Create mock score
    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason="Clear description, recently posted",
    )

    # Generate card
    card_path = generate_card([(score, issue)], "testuser")

    # Verify file was created
    assert card_path.exists()
    assert card_path.suffix == ".png"
    assert "testuser" in str(card_path)

    # Verify image dimensions
    img = Image.open(card_path)
    assert img.size == (1200, 630)
    assert img.mode == "RGB"
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_with_multiple_issues():
    """Test card generation with multiple scored issues."""
    issues = []
    for i in range(3):
        issue = Issue(
            number=i,
            title=f"Issue {i}",
            url=f"https://api.github.com/repos/test/repo/issues/{i}",
            html_url=f"https://github.com/test/repo/issues/{i}",
            body="Test body",
            state="open",
            created_at=datetime.now() - timedelta(days=3),
            updated_at=datetime.now() - timedelta(days=1),
            labels=["good first issue"],
            repo_owner="test",
            repo_name="repo",
            repo_stars=500 * (i + 1),
            repo_language="Python",
            repo_description="Test repo",
            comments=2,
            author="testuser",
        )
        score = IssueScore(
            total_score=0.8 - (i * 0.1),
            clarity_score=0.9,
            maintainer_score=0.8,
            freshness_score=1.0,
            activity_score=0.7,
            reason='Test reason',
        )
        issues.append((score, issue))

    card_path = generate_card(issues, "multiuser")

    assert card_path.exists()

    # Verify image can be opened and has correct dimensions
    img = Image.open(card_path)
    assert img.size == (1200, 630)
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_with_empty_list():
    """Test card generation with no issues."""
    card_path = generate_card([], "emptyuser")

    # Should still create a card
    assert card_path.exists()

    # Verify dimensions
    img = Image.open(card_path)
    assert img.size == (1200, 630)
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_with_long_title():
    """Test card generation with very long issue title."""
    issue = Issue(
        number=1,
        title="This is a very long issue title that should be truncated because it exceeds the maximum character limit for display",
        url="https://api.github.com/repos/test/repo/issues/1",
        html_url="https://github.com/test/repo/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=100,
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason='Clear description, recently posted',
    )

    card_path = generate_card([(score, issue)], "longuser")

    # Should handle long title gracefully
    assert card_path.exists()

    img = Image.open(card_path)
    assert img.size == (1200, 630)
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_with_none_language():
    """Test card generation when repo language is None."""
    issue = Issue(
        number=1,
        title="Test issue",
        url="https://api.github.com/repos/test/repo/issues/1",
        html_url="https://github.com/test/repo/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=100,
        repo_language=None,  # No language specified
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason='Clear description, recently posted',
    )

    card_path = generate_card([(score, issue)], "nolanguser")

    # Should handle None language gracefully (shows "N/A")
    assert card_path.exists()

    img = Image.open(card_path)
    assert img.size == (1200, 630)
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_file_location():
    """Test that card is saved to temp directory."""
    issue = Issue(
        number=1,
        title="Test",
        url="https://api.github.com/repos/test/repo/issues/1",
        html_url="https://github.com/test/repo/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=100,
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason='Clear description, recently posted',
    )

    card_path = generate_card([(score, issue)], "locationuser")

    # Verify it's in temp directory
    import tempfile
    assert str(card_path).startswith(tempfile.gettempdir())

    # Verify filename format
    assert card_path.name == "gfi_results_locationuser.png"

    # Clean up
    card_path.unlink(missing_ok=True)


def test_format_stars_under_1000():
    """Test star formatting for values under 1000."""
    assert _format_stars(0) == "0"
    assert _format_stars(1) == "1"
    assert _format_stars(500) == "500"
    assert _format_stars(999) == "999"


def test_format_stars_over_1000():
    """Test star formatting for values over 1000."""
    assert _format_stars(1000) == "1.0k"
    assert _format_stars(1500) == "1.5k"
    assert _format_stars(5000) == "5.0k"
    assert _format_stars(12345) == "12.3k"


def test_generate_card_with_high_star_count():
    """Test card generation with high star count repo."""
    issue = Issue(
        number=1,
        title="Popular repo issue",
        url="https://api.github.com/repos/test/repo/issues/1",
        html_url="https://github.com/test/repo/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=25000,  # High star count
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason='Clear description, recently posted',
    )

    card_path = generate_card([(score, issue)], "popularuser")

    assert card_path.exists()

    img = Image.open(card_path)
    assert img.size == (1200, 630)
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_image_mode():
    """Test that generated image is in RGB mode."""
    issue = Issue(
        number=1,
        title="Test",
        url="https://api.github.com/repos/test/repo/issues/1",
        html_url="https://github.com/test/repo/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=100,
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason='Clear description, recently posted',
    )

    card_path = generate_card([(score, issue)], "modeuser")

    img = Image.open(card_path)
    assert img.mode == "RGB"  # Should be RGB, not RGBA or other modes
    img.close()

    # Clean up
    card_path.unlink(missing_ok=True)


def test_generate_card_overwrites_existing():
    """Test that generating a card with same username overwrites previous."""
    issue = Issue(
        number=1,
        title="Test",
        url="https://api.github.com/repos/test/repo/issues/1",
        html_url="https://github.com/test/repo/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="repo",
        repo_stars=100,
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    score = IssueScore(
        total_score=0.85,
        clarity_score=0.90,
        maintainer_score=0.80,
        freshness_score=1.0,
        activity_score=0.70,
        reason='Clear description, recently posted',
    )

    # Generate first card
    card_path1 = generate_card([(score, issue)], "overwriteuser")
    first_mtime = card_path1.stat().st_mtime

    # Wait a moment to ensure different timestamp
    import time
    time.sleep(0.1)

    # Generate second card with same username
    card_path2 = generate_card([(score, issue)], "overwriteuser")
    second_mtime = card_path2.stat().st_mtime

    # Should be same path but newer file
    assert card_path1 == card_path2
    assert second_mtime >= first_mtime

    # Clean up
    card_path2.unlink()
