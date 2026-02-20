"""Issue scoring logic."""

from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from .github import GitHubClient, Issue


class IssueScore(BaseModel):
    """Scored issue with breakdown."""
    clarity_score: float  # 0-1
    maintainer_score: float  # 0-1
    freshness_score: float  # 0-1
    activity_score: float  # 0-1
    total_score: float
    reason: str


class IssueScorer:
    """Scores issues based on multiple factors."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def score_issue(self, issue: Issue) -> IssueScore:
        """Score an issue across multiple dimensions."""

        clarity = self._score_clarity(issue)
        maintainer = self._score_maintainer_responsiveness(issue)
        freshness = self._score_freshness(issue)
        activity = self._score_project_activity(issue)

        # Weighted average
        total = (
            clarity * 0.35 +
            maintainer * 0.30 +
            freshness * 0.20 +
            activity * 0.15
        )

        reason = self._generate_reason(clarity, maintainer, freshness, activity)

        return IssueScore(
            clarity_score=clarity,
            maintainer_score=maintainer,
            freshness_score=freshness,
            activity_score=activity,
            total_score=total,
            reason=reason,
        )

    def _score_clarity(self, issue: Issue) -> float:
        """Score issue clarity based on description quality."""
        score = 0.0
        body = (issue.body or "").lower()

        # Has description at all
        if len(body) > 100:
            score += 0.3

        # Has reproduction steps or acceptance criteria
        if any(keyword in body for keyword in ["steps", "reproduce", "acceptance", "criteria", "should", "expected"]):
            score += 0.3

        # Has code snippets or examples
        if "```" in body or "    " in body:
            score += 0.2

        # Not too long (overwhelming)
        if len(body) < 2000:
            score += 0.2

        return min(score, 1.0)

    def _score_maintainer_responsiveness(self, issue: Issue) -> float:
        """Score maintainer responsiveness based on recent issue activity."""
        try:
            # Get recent issues from repo
            recent_issues = self.client.get_repo_issues(
                issue.repo_owner,
                issue.repo_name,
                state="closed",
                limit=10
            )

            if not recent_issues:
                return 0.5  # Neutral if no data

            # Calculate average time to close
            close_times = []
            for recent in recent_issues[:10]:
                if recent.get("closed_at"):
                    created = datetime.fromisoformat(recent["created_at"].rstrip("Z"))
                    closed = datetime.fromisoformat(recent["closed_at"].rstrip("Z"))
                    close_times.append((closed - created).days)

            if not close_times:
                return 0.5

            avg_days = sum(close_times) / len(close_times)

            # Score based on response time
            if avg_days < 7:
                return 1.0
            elif avg_days < 30:
                return 0.7
            elif avg_days < 90:
                return 0.4
            else:
                return 0.2

        except Exception:
            return 0.5  # Neutral on error

    def _score_freshness(self, issue: Issue) -> float:
        """Score based on issue age (sweet spot: 1-30 days)."""
        age_days = (datetime.now() - issue.created_at).days

        if age_days < 1:
            return 0.5  # Too fresh, might be unclear
        elif age_days <= 7:
            return 1.0  # Perfect
        elif age_days <= 30:
            return 0.8
        elif age_days <= 90:
            return 0.5
        else:
            return 0.2  # Might be stale/abandoned

    def _score_project_activity(self, issue: Issue) -> float:
        """Score based on project health indicators."""
        score = 0.0

        # Stars indicate popularity
        if issue.repo_stars > 1000:
            score += 0.4
        elif issue.repo_stars > 100:
            score += 0.3
        elif issue.repo_stars > 50:
            score += 0.2

        # Recent activity (based on issue update)
        days_since_update = (datetime.now() - issue.updated_at).days
        if days_since_update < 7:
            score += 0.3
        elif days_since_update < 30:
            score += 0.2

        # Some comments indicate engagement but not too many (bikeshedding)
        if 1 <= issue.comments <= 5:
            score += 0.3
        elif issue.comments == 0:
            score += 0.1

        return min(score, 1.0)

    def _generate_reason(self, clarity: float, maintainer: float, freshness: float, activity: float) -> str:
        """Generate human-readable reason for score."""
        reasons = []

        if clarity > 0.7:
            reasons.append("Clear description")
        elif clarity < 0.3:
            reasons.append("Vague description")

        if maintainer > 0.7:
            reasons.append("responsive maintainers")
        elif maintainer < 0.3:
            reasons.append("slow response times")

        if freshness > 0.8:
            reasons.append("recently posted")
        elif freshness < 0.3:
            reasons.append("older issue")

        if activity > 0.7:
            reasons.append("active project")

        return ", ".join(reasons) if reasons else "standard issue"
