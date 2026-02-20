"""Export utilities for issue results."""

import json
import csv
from pathlib import Path
from typing import List, Tuple
from .github import Issue
from .scorer import IssueScore


def export_to_json(scored_issues: List[Tuple[IssueScore, Issue]], output_path: Path):
    """Export results to JSON file."""

    results = []
    for score, issue in scored_issues:
        results.append({
            "score": round(score.total_score, 2),
            "clarity_score": round(score.clarity_score, 2),
            "maintainer_score": round(score.maintainer_score, 2),
            "freshness_score": round(score.freshness_score, 2),
            "activity_score": round(score.activity_score, 2),
            "reason": score.reason,
            "title": issue.title,
            "url": issue.html_url,
            "repo": f"{issue.repo_owner}/{issue.repo_name}",
            "language": issue.repo_language,
            "stars": issue.repo_stars,
            "comments": issue.comments,
            "labels": issue.labels,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
        })

    output_path.write_text(json.dumps(results, indent=2))


def export_to_csv(scored_issues: List[Tuple[IssueScore, Issue]], output_path: Path):
    """Export results to CSV file."""

    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Score',
            'Title',
            'URL',
            'Repo',
            'Language',
            'Stars',
            'Comments',
            'Clarity',
            'Maintainer',
            'Freshness',
            'Activity',
            'Reason',
            'Labels',
            'Created',
        ])

        # Data
        for score, issue in scored_issues:
            writer.writerow([
                round(score.total_score, 2),
                issue.title,
                issue.html_url,
                f"{issue.repo_owner}/{issue.repo_name}",
                issue.repo_language or '',
                issue.repo_stars,
                issue.comments,
                round(score.clarity_score, 2),
                round(score.maintainer_score, 2),
                round(score.freshness_score, 2),
                round(score.activity_score, 2),
                score.reason,
                ', '.join(issue.labels[:5]),
                issue.created_at.strftime('%Y-%m-%d'),
            ])
