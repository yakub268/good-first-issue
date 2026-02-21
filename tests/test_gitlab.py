"""Tests for GitLab integration."""

import pytest
from datetime import datetime, timedelta
from gfi.gitlab import GitLabClient, GitLabIssue
from unittest.mock import Mock, MagicMock


def test_gitlab_search_basic():
    """Test basic GitLab search functionality."""
    mock_client = MagicMock()

    # Mock issues response
    mock_issues_response = Mock()
    mock_issues_response.json.return_value = [{
        "iid": 42,
        "title": "Add dark mode",
        "web_url": "https://gitlab.com/test/project/-/issues/42",
        "description": "We need dark mode",
        "state": "opened",
        "created_at": "2026-02-15T10:00:00Z",
        "updated_at": "2026-02-16T10:00:00Z",
        "labels": ["good first issue"],
        "project_id": 123,
        "author": {"username": "testuser"},
        "user_notes_count": 3,
    }]
    mock_issues_response.raise_for_status = Mock()

    # Mock project response
    mock_project_response = Mock()
    mock_project_response.json.return_value = {
        "id": 123,
        "path_with_namespace": "test/project",
        "star_count": 100,
        "description": "Test project",
    }
    mock_project_response.raise_for_status = Mock()

    # Mock languages response
    mock_lang_response = Mock()
    mock_lang_response.json.return_value = {"Python": 80.5, "JavaScript": 19.5}
    mock_lang_response.raise_for_status = Mock()

    # Set up side effects
    mock_client.get.side_effect = [
        mock_issues_response,  # Issues search
        mock_project_response,  # Project details
        mock_lang_response,  # Project languages
    ]

    client = GitLabClient(use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=50,
        max_age_days=30,
        limit=10,
        labels=["good first issue"]  # Search only one label to match mock
    )

    assert len(issues) == 1
    assert issues[0].number == 42
    assert issues[0].title == "Add dark mode"
    assert issues[0].repo_owner == "test"
    assert issues[0].repo_name == "project"


def test_gitlab_filters_by_stars():
    """Test that GitLab client filters by minimum stars."""
    mock_client = MagicMock()

    # Mock issues response
    mock_issues_response = Mock()
    mock_issues_response.json.return_value = [{
        "iid": 42,
        "title": "Test Issue",
        "web_url": "https://gitlab.com/test/project/-/issues/42",
        "description": "Test",
        "state": "opened",
        "created_at": "2026-02-15T10:00:00Z",
        "updated_at": "2026-02-16T10:00:00Z",
        "labels": ["good first issue"],
        "project_id": 123,
        "author": {"username": "testuser"},
        "user_notes_count": 0,
    }]
    mock_issues_response.raise_for_status = Mock()

    # Mock project with low stars
    mock_project_response = Mock()
    mock_project_response.json.return_value = {
        "id": 123,
        "path_with_namespace": "test/project",
        "star_count": 10,  # Below minimum
        "description": "Test project",
    }
    mock_project_response.raise_for_status = Mock()

    mock_lang_response = Mock()
    mock_lang_response.json.return_value = {"Python": 100.0}
    mock_lang_response.raise_for_status = Mock()

    mock_client.get.side_effect = [
        mock_issues_response,
        mock_project_response,
        mock_lang_response,
    ]

    client = GitLabClient(use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=50,  # Higher than project's 10 stars
        max_age_days=30,
        limit=10,
        labels=["good first issue"]  # Search only one label
    )

    # Should filter out the low-star project
    assert len(issues) == 0


def test_gitlab_filters_by_age():
    """Test that GitLab client filters by maximum age."""
    mock_client = MagicMock()

    # Mock old issue
    old_date = (datetime.now() - timedelta(days=60)).isoformat() + "Z"
    mock_issues_response = Mock()
    mock_issues_response.json.return_value = [{
        "iid": 42,
        "title": "Old Issue",
        "web_url": "https://gitlab.com/test/project/-/issues/42",
        "description": "Test",
        "state": "opened",
        "created_at": old_date,  # Too old
        "updated_at": old_date,
        "labels": ["good first issue"],
        "project_id": 123,
        "author": {"username": "testuser"},
        "user_notes_count": 0,
    }]
    mock_issues_response.raise_for_status = Mock()

    mock_client.get.return_value = mock_issues_response

    client = GitLabClient(use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=10,
        max_age_days=30,  # Issue is 60 days old
        limit=10,
        labels=["good first issue"]  # Search only one label
    )

    # Should filter out old issue
    assert len(issues) == 0


def test_gitlab_deduplicates_issues():
    """Test that duplicate issues are removed."""
    mock_client = MagicMock()

    # Same issue in response twice
    duplicate_issue = {
        "iid": 42,
        "title": "Test Issue",
        "web_url": "https://gitlab.com/test/project/-/issues/42",
        "description": "Test",
        "state": "opened",
        "created_at": "2026-02-15T10:00:00Z",
        "updated_at": "2026-02-16T10:00:00Z",
        "labels": ["good first issue", "help wanted"],
        "project_id": 123,
        "author": {"username": "testuser"},
        "user_notes_count": 0,
    }

    mock_issues_response = Mock()
    mock_issues_response.json.return_value = [duplicate_issue, duplicate_issue]
    mock_issues_response.raise_for_status = Mock()

    mock_project_response = Mock()
    mock_project_response.json.return_value = {
        "id": 123,
        "path_with_namespace": "test/project",
        "star_count": 100,
        "description": "Test",
    }
    mock_project_response.raise_for_status = Mock()

    mock_lang_response = Mock()
    mock_lang_response.json.return_value = {"Python": 100.0}
    mock_lang_response.raise_for_status = Mock()

    mock_client.get.side_effect = [
        mock_issues_response,
        mock_project_response,
        mock_lang_response,
    ]

    client = GitLabClient(use_cache=False)
    client.client = mock_client
    client.cache.get = Mock(return_value=None)
    client.cache.set = Mock()

    issues = client.search_good_first_issues(
        languages=["Python"],
        min_stars=10,
        max_age_days=30,
        limit=10,
        labels=["good first issue"]  # Search only one label
    )

    # Should deduplicate
    assert len(issues) == 1
