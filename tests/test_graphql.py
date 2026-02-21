"""Tests for GraphQL client."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from gfi.graphql import GitHubGraphQLClient
from gfi.github import Issue, UserProfile


@pytest.fixture
def mock_graphql_response():
    """Mock GraphQL API response."""
    return {
        "data": {
            "search": {
                "nodes": [
                    {
                        "number": 123,
                        "title": "Test Issue",
                        "url": "https://api.github.com/repos/test/repo/issues/123",
                        "body": "Test description with steps to reproduce and code examples",
                        "state": "OPEN",
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-02T00:00:00Z",
                        "comments": {
                            "totalCount": 5
                        },
                        "labels": {
                            "nodes": [
                                {"name": "good first issue"},
                                {"name": "help wanted"}
                            ]
                        },
                        "author": {
                            "login": "testuser"
                        },
                        "repository": {
                            "owner": {
                                "login": "testowner"
                            },
                            "name": "testrepo",
                            "description": "Test repository",
                            "stargazerCount": 150,
                            "primaryLanguage": {
                                "name": "Python"
                            }
                        }
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_profile_response():
    """Mock user profile GraphQL response."""
    return {
        "data": {
            "user": {
                "login": "testuser",
                "repositories": {
                    "nodes": [
                        {"primaryLanguage": {"name": "Python"}},
                        {"primaryLanguage": {"name": "JavaScript"}},
                        {"primaryLanguage": {"name": "Python"}},
                    ]
                },
                "starredRepositories": {
                    "totalCount": 50,
                    "nodes": [
                        {
                            "primaryLanguage": {"name": "Python"},
                            "repositoryTopics": {
                                "nodes": [
                                    {"topic": {"name": "web"}},
                                    {"topic": {"name": "cli"}}
                                ]
                            }
                        },
                        {
                            "primaryLanguage": {"name": "Rust"},
                            "repositoryTopics": {
                                "nodes": [
                                    {"topic": {"name": "cli"}},
                                ]
                            }
                        }
                    ]
                },
                "contributionsCollection": {
                    "totalRepositoryContributions": 25
                }
            }
        }
    }


def test_graphql_search_issues(mock_graphql_response):
    """Test searching issues with GraphQL."""

    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = mock_graphql_response
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Create client with cache disabled for testing
        client = GitHubGraphQLClient("fake_token", use_cache=False)
        client.client = mock_client

        # Search for issues
        issues = client.search_good_first_issues(
            languages=["Python"],
            min_stars=100,
            max_age_days=30,
            limit=10
        )

        assert len(issues) == 1
        issue = issues[0]
        assert issue.number == 123
        assert issue.title == "Test Issue"
        assert issue.repo_owner == "testowner"
        assert issue.repo_name == "testrepo"
        assert issue.repo_stars == 150
        assert issue.repo_language == "Python"
        assert issue.comments == 5
        assert "good first issue" in issue.labels


def test_graphql_user_profile(mock_profile_response):
    """Test fetching user profile with GraphQL."""

    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = mock_profile_response
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = GitHubGraphQLClient("fake_token", use_cache=False)
        client.client = mock_client

        profile = client.get_user_profile("testuser")

        assert profile.username == "testuser"
        assert "Python" in profile.languages
        assert "cli" in profile.topics
        assert profile.starred_count == 50
        assert profile.contributed_count == 25


def test_graphql_repo_issues():
    """Test fetching repo issues with GraphQL."""

    mock_response = {
        "data": {
            "repository": {
                "issues": {
                    "nodes": [
                        {
                            "number": 1,
                            "title": "Issue 1",
                            "state": "CLOSED",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "closedAt": "2024-01-05T00:00:00Z",
                            "comments": {
                                "totalCount": 3
                            }
                        },
                        {
                            "number": 2,
                            "title": "Issue 2",
                            "state": "OPEN",
                            "createdAt": "2024-01-10T00:00:00Z",
                            "closedAt": None,
                            "comments": {
                                "totalCount": 1
                            }
                        }
                    ]
                }
            }
        }
    }

    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status.return_value = None
        mock_client.post.return_value = mock_resp
        mock_client_class.return_value = mock_client

        client = GitHubGraphQLClient("fake_token", use_cache=False)
        client.client = mock_client

        issues = client.get_repo_issues("test", "repo", limit=100)

        assert len(issues) == 2
        assert issues[0]["number"] == 1
        assert issues[0]["state"] == "closed"
        assert issues[1]["number"] == 2
        assert issues[1]["state"] == "open"


def test_graphql_error_handling():
    """Test GraphQL error handling - errors are caught and logged."""

    error_response = {
        "errors": [
            {"message": "Bad credentials"}
        ]
    }

    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = GitHubGraphQLClient("fake_token", use_cache=False)
        client.client = mock_client

        # search_good_first_issues catches GraphQL errors and continues
        # This is intentional fallback behavior
        issues = client.search_good_first_issues(
            languages=["Python"],
            min_stars=50,
            max_age_days=30,
            limit=10
        )

        # Should return empty list on error
        assert issues == []


def test_graphql_direct_error():
    """Test that _execute_query raises on GraphQL errors."""

    error_response = {
        "errors": [
            {"message": "Bad credentials"}
        ]
    }

    with patch('httpx.Client') as mock_client_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = GitHubGraphQLClient("fake_token", use_cache=False)
        client.client = mock_client

        # _execute_query should raise on GraphQL errors
        with pytest.raises(Exception, match="GraphQL error"):
            client._execute_query("query { test }")
