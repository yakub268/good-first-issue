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

        # Search for issues across multiple languages for diversity
        languages = [language] if language else profile.languages[:3]
        all_issues = []

        for lang in languages:
            try:
                lang_issues = client.search_good_first_issues(
                    languages=[lang],
                    min_stars=20,  # Lower threshold for more variety
                    max_age_days=30,
                    limit=10
                )
                all_issues.extend(lang_issues)
            except:
                continue

        # Remove duplicates
        seen_urls = set()
        unique_issues = []
        for issue in all_issues:
            if issue.html_url not in seen_urls:
                seen_urls.add(issue.html_url)
                unique_issues.append(issue)

        # Score and personalize
        scorer = IssueScorer(client)
        scored_issues = []

        for issue in unique_issues[:30]:  # Score more candidates
            score = scorer.score_issue(issue)
            if score.total_score > 0.3:
                # Boost score if repo topics match user interests
                topic_boost = 0
                if hasattr(profile, 'topics') and profile.topics:
                    # This would require fetching repo topics, skip for now
                    pass

                scored_issues.append({
                    'score': round(score.total_score + topic_boost, 2),
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
        # Log the error but don't expose internal details
        print(f"Error: {e}")  # Server logs
        return jsonify({'error': 'Failed to fetch issues. Please try again later.'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
