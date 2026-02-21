"""Tests for multi-label search functionality."""

import pytest
from datetime import datetime, timedelta
from gfi.github import GitHubClient, Issue
from unittest.mock import Mock, MagicMock


def test_search_with_default_labels(monkeypatch):
    """Test search uses 'good first issue' label by default."""
    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response

    client = GitHubClient("fake_token", use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    # Search without specifying labels
    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=10,
        max_age_days=30,
        limit=10
    )

    # Should search for "good first issue" label
    assert mock_client.get.called
    call_args = mock_client.get.call_args
    query = call_args[1]["params"]["q"]
    assert 'label:"good first issue"' in query


def test_search_with_custom_labels(monkeypatch):
    """Test search with custom labels."""
    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response

    client = GitHubClient("fake_token", use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    # Search with custom labels
    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=10,
        max_age_days=30,
        limit=10,
        labels=["help wanted", "beginner friendly"]
    )

    # Should make multiple queries (one per label)
    assert mock_client.get.call_count == 2  # 1 language × 2 labels

    # Check both labels were queried
    calls = [str(call[1]["params"]["q"]) for call in mock_client.get.call_args_list]
    assert any('label:"help wanted"' in call for call in calls)
    assert any('label:"beginner friendly"' in call for call in calls)


def test_search_deduplicates_across_labels():
    """Test that duplicate issues across label searches are removed."""
    # Create mock data - same issue appears under both labels
    duplicate_issue = {
        "number": 42,
        "title": "Test Issue",
        "url": "https://api.github.com/repos/test/repo/issues/42",
        "html_url": "https://github.com/test/repo/issues/42",
        "body": "Test body",
        "state": "open",
        "created_at": "2026-02-15T10:00:00",
        "updated_at": "2026-02-16T10:00:00",
        "labels": [{"name": "good first issue"}, {"name": "help wanted"}],
        "repository_url": "https://api.github.com/repos/test/repo",
        "user": {"login": "testuser"},
        "comments": 2,
    }

    mock_client = MagicMock()

    # First label returns the issue
    mock_response1 = Mock()
    mock_response1.json.return_value = {"items": [duplicate_issue]}
    mock_response1.raise_for_status = Mock()

    # Second label also returns same issue
    mock_response2 = Mock()
    mock_response2.json.return_value = {"items": [duplicate_issue]}
    mock_response2.raise_for_status = Mock()

    # Mock repo response
    mock_repo_response = Mock()
    mock_repo_response.json.return_value = {
        "stargazers_count": 100,
        "language": "Python",
        "description": "Test repo",
    }
    mock_repo_response.raise_for_status = Mock()

    # Return different responses based on call
    mock_client.get.side_effect = [
        mock_response1,  # First label search
        mock_repo_response,  # Repo details
        mock_response2,  # Second label search
        # No second repo call because it's cached/duplicate
    ]

    client = GitHubClient("fake_token", use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    # Search with two labels
    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=10,
        max_age_days=30,
        limit=10,
        labels=["good first issue", "help wanted"]
    )

    # Should only return one issue (deduplicated)
    assert len(issues) == 1
    assert issues[0].number == 42


def test_search_with_multiple_languages_and_labels():
    """Test search combines languages and labels correctly."""
    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response

    client = GitHubClient("fake_token", use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    # Search with 2 languages and 2 labels
    issues = client.search_good_first_issues(
        languages=["Python", "JavaScript"],
        min_stars=10,
        max_age_days=30,
        limit=10,
        labels=["good first issue", "help wanted"]
    )

    # Should make 4 queries (2 languages × 2 labels)
    assert mock_client.get.call_count == 4


def test_labels_parameter_optional():
    """Test that labels parameter is optional and defaults correctly."""
    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response

    client = GitHubClient("fake_token", use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    # Call without labels parameter
    issues = client.search_good_first_issues(
        languages=["Python"],
    )

    # Should still work and use default label
    assert mock_client.get.called
    query = mock_client.get.call_args[1]["params"]["q"]
    assert 'label:"good first issue"' in query
