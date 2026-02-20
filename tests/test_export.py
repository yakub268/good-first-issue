"""Tests for export functionality."""

import json
import csv
from pathlib import Path
from datetime import datetime
from gfi.export import export_to_json, export_to_csv
from gfi.github import Issue
from gfi.scorer import IssueScore


def test_export_to_json(tmp_path):
    """Test JSON export."""

    # Create mock data
    issue = Issue(
        number=1,
        title="Test issue",
        body="Test body",
        html_url="https://github.com/test/repo/issues/1",
        url="https://api.github.com/repos/test/repo/issues/1",
        state="open",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
        labels=["good first issue"],
        comments=5,
        repo_owner="test",
        repo_name="repo",
        repo_description="Test repo",
        repo_stars=100,
        repo_language="Python",
        author="testuser"
    )

    score = IssueScore(
        clarity_score=0.8,
        maintainer_score=0.7,
        freshness_score=0.9,
        activity_score=0.6,
        total_score=0.75,
        reason="Test reason"
    )

    scored_issues = [(score, issue)]
    output_path = tmp_path / "test.json"

    # Export
    export_to_json(scored_issues, output_path)

    # Verify
    assert output_path.exists()
    data = json.loads(output_path.read_text())
    assert len(data) == 1
    assert data[0]["score"] == 0.75
    assert data[0]["title"] == "Test issue"
    assert data[0]["repo"] == "test/repo"


def test_export_to_csv(tmp_path):
    """Test CSV export."""

    issue = Issue(
        number=1,
        title="Test issue",
        body="Test body",
        html_url="https://github.com/test/repo/issues/1",
        url="https://api.github.com/repos/test/repo/issues/1",
        state="open",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
        labels=["good first issue"],
        comments=5,
        repo_owner="test",
        repo_name="repo",
        repo_description="Test repo",
        repo_stars=100,
        repo_language="Python",
        author="testuser"
    )

    score = IssueScore(
        clarity_score=0.8,
        maintainer_score=0.7,
        freshness_score=0.9,
        activity_score=0.6,
        total_score=0.75,
        reason="Test reason"
    )

    scored_issues = [(score, issue)]
    output_path = tmp_path / "test.csv"

    # Export
    export_to_csv(scored_issues, output_path)

    # Verify
    assert output_path.exists()

    with output_path.open('r') as f:
        reader = csv.reader(f)
        rows = list(reader)

        assert len(rows) == 2  # Header + 1 data row
        assert rows[0][0] == 'Score'
        assert rows[1][0] == '0.75'
        assert rows[1][1] == 'Test issue'


def test_export_multiple_issues(tmp_path):
    """Test exporting multiple issues."""

    issues = []
    for i in range(3):
        issue = Issue(
            number=i,
            title=f"Issue {i}",
            body="Body",
            html_url=f"https://github.com/test/repo/issues/{i}",
            url=f"https://api.github.com/repos/test/repo/issues/{i}",
            state="open",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
            labels=["good first issue"],
            comments=i,
            repo_owner="test",
            repo_name="repo",
            repo_description="Test repo",
            repo_stars=100,
            repo_language="Python",
            author="testuser"
        )

        score = IssueScore(
            clarity_score=0.8,
            maintainer_score=0.7,
            freshness_score=0.9,
            activity_score=0.6,
            total_score=0.7 + (i * 0.1),
            reason="Test"
        )

        issues.append((score, issue))

    output_path = tmp_path / "test.json"
    export_to_json(issues, output_path)

    data = json.loads(output_path.read_text())
    assert len(data) == 3
    assert data[0]["score"] == 0.7
    assert data[2]["score"] == 0.9
