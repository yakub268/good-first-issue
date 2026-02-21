"""GitLab API client."""

import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from .cache import DiskCache


class GitLabIssue(BaseModel):
    """GitLab issue model - compatible with GitHub Issue."""
    number: int
    title: str
    url: str
    html_url: str
    body: Optional[str]
    state: str
    created_at: datetime
    updated_at: datetime
    labels: List[str]
    repo_owner: str  # Project namespace
    repo_name: str  # Project path
    repo_stars: int  # Star count
    repo_language: Optional[str]
    repo_description: Optional[str]
    comments: int
    author: str


class GitLabClient:
    """GitLab API client with rate limiting and caching."""

    BASE_URL = "https://gitlab.com/api/v4"

    def __init__(self, token: Optional[str] = None, use_cache: bool = True):
        """Initialize GitLab client.

        Args:
            token: GitLab personal access token (optional for public data)
            use_cache: Whether to use disk cache
        """
        headers = {"Accept": "application/json"}
        if token:
            headers["PRIVATE-TOKEN"] = token

        self.client = httpx.Client(
            headers=headers,
            timeout=30.0,
        )
        self.cache = DiskCache(enabled=use_cache)

    def search_good_first_issues(
        self,
        languages: List[str],
        min_stars: int = 50,
        max_age_days: int = 30,
        limit: int = 30,
        labels: Optional[List[str]] = None,
    ) -> List[GitLabIssue]:
        """Search for good first issues on GitLab.

        Args:
            languages: List of programming languages (note: GitLab search by language is limited)
            min_stars: Minimum project star count
            max_age_days: Maximum issue age in days
            limit: Maximum number of results
            labels: Issue labels to search for (defaults to ["good first issue"])
        """
        if labels is None:
            labels = ["good first issue", "help wanted", "beginner friendly"]

        issues = []
        seen_urls = set()
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        for label in labels:
            # GitLab search query
            # Note: GitLab doesn't support language filtering in issue search like GitHub
            # We'll filter by language after fetching project details

            # Check cache first
            cache_key = f"gitlab:search:{label}:{min_stars}:{limit}"
            cached_data = self.cache.get(cache_key, self.cache.SEARCH_TTL_MINUTES)

            if cached_data is not None:
                search_results = cached_data
            else:
                # Search issues with label
                response = self.client.get(
                    f"{self.BASE_URL}/issues",
                    params={
                        "labels": label,
                        "state": "opened",
                        "scope": "all",  # Search all GitLab
                        "per_page": min(100, limit * 2),  # Get more to filter
                    }
                )
                response.raise_for_status()
                search_results = response.json()
                self.cache.set(cache_key, search_results)

            for item in search_results:
                # Skip duplicates
                issue_url = item["web_url"]
                if issue_url in seen_urls:
                    continue

                # Check age
                created_at = datetime.fromisoformat(item["created_at"].rstrip("Z"))
                if created_at < cutoff_date:
                    continue

                # Get project details
                project_id = item["project_id"]
                project = self._get_project(project_id)

                if not project:
                    continue

                # Filter by stars and language
                if project.get("star_count", 0) < min_stars:
                    continue

                # Language filtering (if languages specified)
                project_lang = project.get("languages", {})
                if languages and project_lang:
                    # Get primary language (highest percentage)
                    primary_lang = max(project_lang.items(), key=lambda x: x[1])[0] if project_lang else None
                    if primary_lang not in languages:
                        continue

                seen_urls.add(issue_url)

                # Parse project namespace and path
                project_path_with_namespace = project["path_with_namespace"]
                parts = project_path_with_namespace.split("/")
                namespace = "/".join(parts[:-1]) if len(parts) > 1 else parts[0]
                project_name = parts[-1]

                issues.append(GitLabIssue(
                    number=item["iid"],  # Internal ID (per-project)
                    title=item["title"],
                    url=item["web_url"],
                    html_url=item["web_url"],
                    body=item.get("description", ""),
                    state=item["state"],
                    created_at=created_at,
                    updated_at=datetime.fromisoformat(item["updated_at"].rstrip("Z")),
                    labels=item.get("labels", []),
                    repo_owner=namespace,
                    repo_name=project_name,
                    repo_stars=project.get("star_count", 0),
                    repo_language=max(project_lang.items(), key=lambda x: x[1])[0] if project_lang else None,
                    repo_description=project.get("description"),
                    comments=item.get("user_notes_count", 0),
                    author=item["author"]["username"],
                ))

                if len(issues) >= limit:
                    break

            if len(issues) >= limit:
                break

        return issues[:limit]

    def _get_project(self, project_id: int) -> Optional[dict]:
        """Get project details by ID."""
        cache_key = f"gitlab:project:{project_id}"
        cached = self.cache.get(cache_key, 60)  # Cache for 1 hour

        if cached is not None:
            return cached

        try:
            response = self.client.get(f"{self.BASE_URL}/projects/{project_id}")
            response.raise_for_status()
            project = response.json()

            # Get project languages
            try:
                lang_response = self.client.get(f"{self.BASE_URL}/projects/{project_id}/languages")
                lang_response.raise_for_status()
                project["languages"] = lang_response.json()
            except:
                project["languages"] = {}

            self.cache.set(cache_key, project)
            return project
        except:
            return None
