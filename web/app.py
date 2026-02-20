"""Web interface for Good First Issue Finder."""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

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
        profile = analyzer.build_profile(username)

        # Search for issues
        languages = [language] if language else profile.languages[:2]
        issues = client.search_good_first_issues(
            languages=languages,
            min_stars=50,
            max_age_days=30,
            limit=15
        )

        # Score issues
        scorer = IssueScorer(client)
        scored_issues = []
        for issue in issues[:10]:
            score = scorer.score_issue(issue)
            if score.total_score > 0.3:
                scored_issues.append({
                    'score': round(score.total_score, 2),
                    'title': issue.title,
                    'repo': f"{issue.repo_owner}/{issue.repo_name}",
                    'url': issue.html_url,
                    'language': issue.repo_language,
                    'stars': issue.repo_stars,
                    'reason': score.reason,
                })

        # Sort by score
        scored_issues.sort(key=lambda x: x['score'], reverse=True)

        return jsonify({
            'username': username,
            'languages': languages,
            'issues': scored_issues[:5],  # Top 5
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
