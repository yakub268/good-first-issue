"""Profile analyzer to understand user interests."""

from collections import Counter
from typing import List, Union
from .github import GitHubClient, UserProfile


class ProfileAnalyzer:
    """Analyzes a user's GitHub activity to build interest profile."""

    def __init__(self, client: Union[GitHubClient, 'GitHubGraphQLClient']):
        self.client = client

    def build_profile(self, username: str = None) -> UserProfile:
        """Build user profile from GitHub activity."""

        # Check if using GraphQL client
        from .graphql import GitHubGraphQLClient
        if isinstance(self.client, GitHubGraphQLClient):
            if username is None:
                # For GraphQL, we need username upfront
                # Fall back to getting from REST
                raise ValueError("Username required for GraphQL profile analysis")
            return self.client.get_user_profile(username)

        # REST API path (original implementation)
        if username is None:
            user = self.client.get_user()
            username = user["login"]

        # Get starred repos
        starred = self.client.get_user_starred(username)

        # Get user's own repos
        own_repos = self.client.get_user_repos(username)

        # Extract languages
        languages = []
        for repo in starred + own_repos:
            if repo.get("language"):
                languages.append(repo["language"])

        # Count language frequency
        lang_counts = Counter(languages)
        top_languages = [lang for lang, _ in lang_counts.most_common(10)]

        # Extract topics from starred repos
        topics = []
        for repo in starred:
            topics.extend(repo.get("topics", []))

        topic_counts = Counter(topics)
        top_topics = [topic for topic, _ in topic_counts.most_common(20)]

        return UserProfile(
            username=username,
            languages=top_languages,
            topics=top_topics,
            starred_count=len(starred),
            contributed_count=len(own_repos),
        )
