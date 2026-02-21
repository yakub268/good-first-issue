"""Debug script to test the API locally."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gfi.github import GitHubClient, Issue
from gfi.analyzer import ProfileAnalyzer
from gfi.scorer import IssueScorer
import os
from datetime import datetime
import hashlib

# Get token
token = os.getenv('GITHUB_TOKEN')
if not token:
    print("ERROR: GITHUB_TOKEN not set")
    sys.exit(1)

username = 'torvalds'
print(f"\n=== Testing for username: {username} ===\n")

# Build profile
client = GitHubClient(token)
analyzer = ProfileAnalyzer(client)
profile = analyzer.build_profile(username)

print(f"Languages: {profile.languages}")

# Search
user_hash = int(hashlib.md5(username.encode()).hexdigest()[:8], 16)
languages = profile.languages[:1]
all_issues = []

label_sets = [
    ['good first issue', 'good-first-issue'],
    ['help wanted', 'help-wanted'],
    ['beginner friendly', 'beginner', 'easy'],
]

labels_to_search = label_sets[user_hash % len(label_sets)]
print(f"Label set (hash {user_hash % len(label_sets)}): {labels_to_search}")

for lang in languages:
    for label in labels_to_search:
        query = f'label:"{label}" language:{lang} state:open'
        print(f"\nQuery: {query}")

        try:
            response = client.client.get(
                "https://api.github.com/search/issues",
                params={
                    'q': query,
                    'sort': 'created',
                    'order': 'desc',
                    'per_page': 20
                }
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                items = response.json().get('items', [])
                print(f"Items found: {len(items)}")

                for item in items[:3]:  # Just check first 3
                    print(f"\n  Issue #{item['number']}: {item['title'][:50]}")
                    print(f"  Created: {item['created_at']}")
                    print(f"  Updated: {item['updated_at']}")

                    try:
                        issue = Issue(
                            number=item['number'],
                            title=item['title'],
                            url=item['url'],
                            html_url=item['html_url'],
                            body=item.get('body'),
                            state=item['state'],
                            created_at=datetime.fromisoformat(item['created_at'].rstrip("Z")),
                            updated_at=datetime.fromisoformat(item['updated_at'].rstrip("Z")),
                            labels=[l['name'] for l in item.get('labels', [])],
                            repo_owner=item['repository_url'].split('/')[-2],
                            repo_name=item['repository_url'].split('/')[-1],
                            repo_stars=0,
                            repo_language=lang,
                            repo_description=None,
                            comments=item.get('comments', 0),
                            author=item.get('user', {}).get('login', 'unknown')
                        )
                        print(f"  ✓ Parsed successfully")
                        all_issues.append(issue)
                    except Exception as e:
                        print(f"  ✗ Parse error: {e}")
            else:
                print(f"Error response: {response.text[:200]}")

        except Exception as e:
            print(f"Request error: {e}")

print(f"\n=== Total issues collected: {len(all_issues)} ===")

# Dedup
seen_urls = set()
unique_issues = []
for issue in all_issues:
    if issue.html_url not in seen_urls:
        seen_urls.add(issue.html_url)
        unique_issues.append(issue)

print(f"Unique issues: {len(unique_issues)}")

# Score
scorer = IssueScorer(client)
scored_issues = []
threshold = 0.25 + (user_hash % 10) * 0.01

print(f"\nScoring threshold: {threshold}")

for issue in unique_issues[:10]:
    score = scorer.score_issue(issue)
    print(f"\n{issue.title[:50]}")
    print(f"  Score: {score.total_score:.3f} (threshold: {threshold:.3f})")
    print(f"  Reason: {score.reason}")

    if score.total_score > threshold:
        print(f"  ✓ PASSED")
        scored_issues.append(issue)
    else:
        print(f"  ✗ FILTERED OUT")

print(f"\n=== Final result: {len(scored_issues)} issues passed scoring ===")
