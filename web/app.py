"""Web interface for Good First Issue Finder."""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import gfi modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from gfi.github import GitHubClient
from gfi.analyzer import ProfileAnalyzer
from gfi.scorer import IssueScorer
import os

app = Flask(__name__)


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/find', methods=['POST'])
def find_issues():
    """API endpoint to find issues for a GitHub username."""

    data = request.json
    username = data.get('username')
    language = data.get('language', '')

    if not username:
        return jsonify({'error': 'Username required'}), 400

    # Use demo token for instant mode (read-only, rate-limited)
    # Users should still run CLI with their own token for full features
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        return jsonify({'error': 'Service temporarily unavailable'}), 503

    try:
        client = GitHubClient(token)
        analyzer = ProfileAnalyzer(client)

        # Build quick profile
        try:
            profile = analyzer.build_profile(username)
        except Exception as e:
            return jsonify({'error': f'Username "{username}" not found or profile is private'}), 404

        # Check if we have any languages
        if not profile.languages:
            return jsonify({
                'username': username,
                'languages': [],
                'issues': [],
                'message': 'No public repositories found. Try starring some repos or making your profile public.'
            })

        # Search multiple label types for much more variety
        import hashlib
        user_hash = int(hashlib.md5(username.encode()).hexdigest()[:8], 16)

        languages = [language] if language else profile.languages[:1]  # Focus on top language
        all_issues = []

        # Different users get different label searches
        label_sets = [
            ['good first issue', 'good-first-issue'],
            ['help wanted', 'help-wanted'],
            ['beginner friendly', 'beginner', 'easy'],
        ]

        # Pick label set based on user hash
        labels_to_search = label_sets[user_hash % len(label_sets)]
        print(f"[{username}] Searching with labels: {labels_to_search}")

        # Build custom search query
        for lang in languages:
            for label in labels_to_search:
                query = f'label:"{label}" language:{lang} state:open'

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

                    if response.status_code == 200:
                        items = response.json().get('items', [])
                        print(f"[{username}] Query '{query}' returned {len(items)} items")

                        for item in items:
                            # Convert to Issue object
                            from gfi.github import Issue
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
                                    repo_stars=0,  # Will score anyway
                                    repo_language=lang,
                                    repo_description=None,
                                    comments=item.get('comments', 0),
                                    author=item.get('user', {}).get('login', 'unknown')
                                )
                                all_issues.append(issue)
                            except Exception as e:
                                print(f"[{username}] Error parsing issue {item.get('number', '?')}: {e}")
                    else:
                        print(f"[{username}] GitHub API error {response.status_code}: {response.text[:100]}")

                except Exception as e:
                    print(f"[{username}] Request error: {e}")
                    continue

                if len(all_issues) >= 30:
                    break

        print(f"[{username}] Total issues collected: {len(all_issues)}")

        # Remove duplicates
        seen_urls = set()
        unique_issues = []
        for issue in all_issues:
            if issue.html_url not in seen_urls:
                seen_urls.add(issue.html_url)
                unique_issues.append(issue)

        print(f"[{username}] Unique issues: {len(unique_issues)}")

        # Score and personalize
        scorer = IssueScorer(client)
        scored_issues = []

        # Vary threshold slightly by user for diversity
        threshold = 0.25 + (user_hash % 10) * 0.01  # 0.25-0.34
        print(f"[{username}] Scoring threshold: {threshold:.3f}")

        for issue in unique_issues[:40]:
            score = scorer.score_issue(issue)

            if score.total_score > threshold:
                scored_issues.append({
                    'score': round(score.total_score, 2),
                    'title': issue.title,
                    'repo': f"{issue.repo_owner}/{issue.repo_name}",
                    'url': issue.html_url,
                    'language': issue.repo_language,
                    'stars': issue.repo_stars,
                    'reason': score.reason,
                })

        # Sort by score and take top N (vary N by user)
        scored_issues.sort(key=lambda x: x['score'], reverse=True)
        result_count = 5 + (user_hash % 3)  # 5, 6, or 7 results

        print(f"[{username}] Final results: {len(scored_issues)} issues passed scoring")

        return jsonify({
            'username': username,
            'languages': languages,
            'issues': scored_issues[:result_count],
        })

    except Exception as e:
        # Log the error but don't expose internal details
        print(f"Error: {e}")  # Server logs
        return jsonify({'error': 'Failed to fetch issues. Please try again later.'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
