"""GitHub API client."""

import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel


class Issue(BaseModel):
    """GitHub issue model."""
    number: int
    title: str
    url: str
    html_url: str
    body: Optional[str]
    state: str
    created_at: datetime
    updated_at: datetime
    labels: List[str]
    repo_owner: str
    repo_name: str
    repo_stars: int
    repo_language: Optional[str]
    repo_description: Optional[str]
    comments: int
    author: str


class UserProfile(BaseModel):
    """User profile information."""
    username: str
    languages: List[str]
    topics: List[str]
    starred_count: int
    contributed_count: int


class GitHubClient:
    """GitHub API client with rate limiting and caching."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30.0,
        )

    def get_user(self) -> dict:
        """Get authenticated user info."""
        response = self.client.get(f"{self.BASE_URL}/user")
        response.raise_for_status()
        return response.json()

    def get_user_starred(self, username: str, per_page: int = 100) -> List[dict]:
        """Get user's starred repositories."""
        repos = []
        page = 1

        while len(repos) < 200:  # Cap at 200 for speed
            response = self.client.get(
                f"{self.BASE_URL}/users/{username}/starred",
                params={"per_page": per_page, "page": page}
            )
            response.raise_for_status()
            batch = response.json()

            if not batch:
                break

            repos.extend(batch)
            page += 1

        return repos

    def get_user_repos(self, username: str) -> List[dict]:
        """Get user's repositories."""
        response = self.client.get(
            f"{self.BASE_URL}/users/{username}/repos",
            params={"per_page": 100, "sort": "updated"}
        )
        response.raise_for_status()
        return response.json()

    def search_good_first_issues(
        self,
        languages: List[str],
        min_stars: int = 50,
        max_age_days: int = 30,
        limit: int = 30,
    ) -> List[Issue]:
        """Search for good first issues."""

        issues = []
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        for language in languages:
            # Build search query
            query_parts = [
                "is:issue",
                "is:open",
                'label:"good first issue"',
                f"language:{language}",
                f"stars:>={min_stars}",
                f"created:>={cutoff_date.strftime('%Y-%m-%d')}",
            ]
            query = " ".join(query_parts)

            response = self.client.get(
                f"{self.BASE_URL}/search/issues",
                params={
                    "q": query,
                    "sort": "created",
                    "order": "desc",
                    "per_page": min(100, limit),
                }
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                # Parse repo info from URL
                repo_url = item["repository_url"]
                repo_parts = repo_url.split("/")
                owner = repo_parts[-2]
                repo_name = repo_parts[-1]

                # Get repo details
                repo = self.get_repo(owner, repo_name)

                issues.append(Issue(
                    number=item["number"],
                    title=item["title"],
                    url=item["url"],
                    html_url=item["html_url"],
                    body=item.get("body", ""),
                    state=item["state"],
                    created_at=datetime.fromisoformat(item["created_at"].rstrip("Z")),
                    updated_at=datetime.fromisoformat(item["updated_at"].rstrip("Z")),
                    labels=[label["name"] for label in item.get("labels", [])],
                    repo_owner=owner,
                    repo_name=repo_name,
                    repo_stars=repo.get("stargazers_count", 0),
                    repo_language=repo.get("language"),
                    repo_description=repo.get("description"),
                    comments=item.get("comments", 0),
                    author=item["user"]["login"],
                ))

        return issues

    def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository details."""
        response = self.client.get(f"{self.BASE_URL}/repos/{owner}/{repo}")
        response.raise_for_status()
        return response.json()

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Issue:
        """Get specific issue details."""
        response = self.client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}")
        response.raise_for_status()
        item = response.json()

        repo_data = self.get_repo(owner, repo)

        return Issue(
            number=item["number"],
            title=item["title"],
            url=item["url"],
            html_url=item["html_url"],
            body=item.get("body", ""),
            state=item["state"],
            created_at=datetime.fromisoformat(item["created_at"].rstrip("Z")),
            updated_at=datetime.fromisoformat(item["updated_at"].rstrip("Z")),
            labels=[label["name"] for label in item.get("labels", [])],
            repo_owner=owner,
            repo_name=repo,
            repo_stars=repo_data.get("stargazers_count", 0),
            repo_language=repo_data.get("language"),
            repo_description=repo_data.get("description"),
            comments=item.get("comments", 0),
            author=item["user"]["login"],
        )

    def get_repo_issues(self, owner: str, repo: str, state: str = "all", limit: int = 100) -> List[dict]:
        """Get recent issues from a repo (for analyzing maintainer responsiveness)."""
        response = self.client.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": limit, "sort": "updated", "direction": "desc"}
        )
        response.raise_for_status()
        return response.json()

    def __del__(self):
        """Clean up HTTP client."""
        self.client.close()
