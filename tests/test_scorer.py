"""Tests for issue scoring logic."""

import pytest
from datetime import datetime, timedelta
from gfi.scorer import IssueScorer
from gfi.github import Issue


def test_clarity_score_good_description():
    """Test clarity scoring with a good description."""
    issue = Issue(
        number=1,
        title="Add feature X",
        url="https://api.github.com/repos/test/test/issues/1",
        html_url="https://github.com/test/test/issues/1",
        body="""
        ## Steps to reproduce
        1. Do this
        2. Do that

        ## Expected behavior
        Should work like this

        ```python
        example_code()
        ```
        """,
        state="open",
        created_at=datetime.now() - timedelta(days=3),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="test",
        repo_stars=500,
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    scorer = IssueScorer(None)
    clarity = scorer._score_clarity(issue)

    assert clarity >= 0.8  # Should score high


def test_freshness_score_sweet_spot():
    """Test freshness scoring for ideal age."""
    issue = Issue(
        number=1,
        title="Test",
        url="https://api.github.com/repos/test/test/issues/1",
        html_url="https://github.com/test/test/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=7),  # Perfect age
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="test",
        repo_stars=500,
        repo_language="Python",
        repo_description="Test repo",
        comments=2,
        author="testuser",
    )

    scorer = IssueScorer(None)
    freshness = scorer._score_freshness(issue)

    assert freshness == 1.0  # Perfect score


def test_project_activity_popular_repo():
    """Test activity scoring for popular repos."""
    issue = Issue(
        number=1,
        title="Test",
        url="https://api.github.com/repos/test/test/issues/1",
        html_url="https://github.com/test/test/issues/1",
        body="Test body",
        state="open",
        created_at=datetime.now() - timedelta(days=7),
        updated_at=datetime.now() - timedelta(days=1),
        labels=["good first issue"],
        repo_owner="test",
        repo_name="test",
        repo_stars=5000,  # Popular
        repo_language="Python",
        repo_description="Test repo",
        comments=3,  # Healthy engagement
        author="testuser",
    )

    scorer = IssueScorer(None)
    activity = scorer._score_project_activity(issue)

    assert activity >= 0.8  # Should score high
