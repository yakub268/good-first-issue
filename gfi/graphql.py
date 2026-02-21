"""GitHub GraphQL API client for better performance."""

import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .github import Issue, UserProfile
from .cache import DiskCache


class GitHubGraphQLClient:
    """GitHub GraphQL API client - more efficient than REST API."""

    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str, use_cache: bool = True):
        self.token = token
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        self.cache = DiskCache(enabled=use_cache)

    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> dict:
        """Execute a GraphQL query."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = self.client.post(self.GRAPHQL_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL error: {data['errors']}")

        return data["data"]

    def get_user_profile(self, username: str) -> UserProfile:
        """Get user profile with starred repos using GraphQL."""

        query = """
        query($username: String!, $starredFirst: Int!) {
          user(login: $username) {
            login
            repositories(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
              nodes {
                primaryLanguage {
                  name
                }
              }
            }
            starredRepositories(first: $starredFirst) {
              totalCount
              nodes {
                primaryLanguage {
                  name
                }
                repositoryTopics(first: 10) {
                  nodes {
                    topic {
                      name
                    }
                  }
                }
              }
            }
            contributionsCollection {
              totalRepositoryContributions
            }
          }
        }
        """

        # Check cache
        cache_key = f"graphql:profile:{username}"
        cached_data = self.cache.get(cache_key, 60)  # 60 minutes TTL
        if cached_data is not None:
            return UserProfile(**cached_data)

        data = self._execute_query(query, {"username": username, "starredFirst": 200})
        user = data["user"]

        # Extract languages from owned repos
        languages = {}
        for repo in user["repositories"]["nodes"]:
            if repo["primaryLanguage"]:
                lang = repo["primaryLanguage"]["name"]
                languages[lang] = languages.get(lang, 0) + 1

        # Extract languages and topics from starred repos
        topics = {}
        for repo in user["starredRepositories"]["nodes"]:
            if repo["primaryLanguage"]:
                lang = repo["primaryLanguage"]["name"]
                languages[lang] = languages.get(lang, 0) + 1

            for topic_node in repo["repositoryTopics"]["nodes"]:
                topic = topic_node["topic"]["name"]
                topics[topic] = topics.get(topic, 0) + 1

        # Sort by frequency
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)

        profile = UserProfile(
            username=user["login"],
            languages=[lang for lang, _ in sorted_languages[:10]],
            topics=[topic for topic, _ in sorted_topics[:10]],
            starred_count=user["starredRepositories"]["totalCount"],
            contributed_count=user["contributionsCollection"]["totalRepositoryContributions"],
        )

        # Cache the profile
        self.cache.set(cache_key, profile.model_dump())
        return profile

    def search_good_first_issues(
        self,
        languages: List[str],
        min_stars: int = 50,
        max_age_days: int = 30,
        limit: int = 30,
        labels: Optional[List[str]] = None,
    ) -> List[Issue]:
        """Search for good first issues using GraphQL.

        More efficient than REST API - fetches issue and repo data in one query.
        """
        if labels is None:
            labels = ["good first issue"]

        issues = []
        seen_urls = set()
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        query = """
        query($searchQuery: String!, $limit: Int!) {
          search(query: $searchQuery, type: ISSUE, first: $limit) {
            nodes {
              ... on Issue {
                number
                title
                url
                body
                state
                createdAt
                updatedAt
                comments {
                  totalCount
                }
                labels(first: 10) {
                  nodes {
                    name
                  }
                }
                author {
                  login
                }
                repository {
                  owner {
                    login
                  }
                  name
                  description
                  stargazerCount
                  primaryLanguage {
                    name
                  }
                }
              }
            }
          }
        }
        """

        for language in languages:
            for label in labels:
                # Build search query
                query_parts = [
                    "is:issue",
                    "is:open",
                    f'label:"{label}"',
                    f"language:{language}",
                    f"stars:>={min_stars}",
                    f"created:>={cutoff_date.strftime('%Y-%m-%d')}",
                    "sort:created-desc",
                ]
                search_query = " ".join(query_parts)

                # Check cache
                cache_key = f"graphql:search:{search_query}:{limit}"
                cached_data = self.cache.get(cache_key, self.cache.SEARCH_TTL_MINUTES)

                if cached_data is not None:
                    result_issues = [Issue(**issue_data) for issue_data in cached_data]
                    for issue in result_issues:
                        if issue.html_url not in seen_urls:
                            seen_urls.add(issue.html_url)
                            issues.append(issue)
                    continue

                try:
                    data = self._execute_query(query, {
                        "searchQuery": search_query,
                        "limit": min(100, limit)
                    })

                    cache_items = []
                    for node in data["search"]["nodes"]:
                        if not node:  # Skip null nodes
                            continue

                        repo = node["repository"]
                        owner = repo["owner"]["login"]
                        repo_name = repo["name"]
                        html_url = f"https://github.com/{owner}/{repo_name}/issues/{node['number']}"

                        # Skip duplicates
                        if html_url in seen_urls:
                            continue
                        seen_urls.add(html_url)

                        issue = Issue(
                            number=node["number"],
                            title=node["title"],
                            url=node["url"],
                            html_url=html_url,
                            body=node.get("body", ""),
                            state=node["state"].lower(),
                            created_at=datetime.fromisoformat(node["createdAt"].rstrip("Z")),
                            updated_at=datetime.fromisoformat(node["updatedAt"].rstrip("Z")),
                            labels=[lbl["name"] for lbl in node["labels"]["nodes"]],
                            repo_owner=owner,
                            repo_name=repo_name,
                            repo_stars=repo["stargazerCount"],
                            repo_language=repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else None,
                            repo_description=repo.get("description"),
                            comments=node["comments"]["totalCount"],
                            author=node["author"]["login"] if node["author"] else "unknown",
                        )

                        issues.append(issue)
                        cache_items.append(issue.model_dump())

                    # Cache the results
                    self.cache.set(cache_key, cache_items)

                except Exception as e:
                    # Fall back to REST API on error
                    print(f"GraphQL query failed for {language}/{label}: {e}")
                    continue

        return issues

    def get_repo_issues(self, owner: str, repo: str, limit: int = 100) -> List[dict]:
        """Get recent issues from a repo using GraphQL."""

        query = """
        query($owner: String!, $repo: String!, $limit: Int!) {
          repository(owner: $owner, name: $repo) {
            issues(first: $limit, orderBy: {field: UPDATED_AT, direction: DESC}, states: [OPEN, CLOSED]) {
              nodes {
                number
                title
                state
                createdAt
                closedAt
                comments {
                  totalCount
                }
              }
            }
          }
        }
        """

        # Check cache
        cache_key = f"graphql:repo-issues:{owner}/{repo}"
        cached_data = self.cache.get(cache_key, self.cache.REPO_TTL_MINUTES)
        if cached_data is not None:
            return cached_data

        data = self._execute_query(query, {
            "owner": owner,
            "repo": repo,
            "limit": limit
        })

        issues = []
        for node in data["repository"]["issues"]["nodes"]:
            issues.append({
                "number": node["number"],
                "title": node["title"],
                "state": node["state"].lower(),
                "created_at": node["createdAt"],
                "closed_at": node.get("closedAt"),
                "comments": node["comments"]["totalCount"],
            })

        # Cache the results
        self.cache.set(cache_key, issues)
        return issues

    def __del__(self):
        """Clean up HTTP client."""
        self.client.close()
