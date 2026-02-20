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

        # Search for issues - vary by user's profile hash for diversity
        import hashlib
        user_hash = int(hashlib.md5(username.encode()).hexdigest()[:8], 16)

        languages = [language] if language else profile.languages[:3]
        all_issues = []

        # Search across languages with different age windows for variety
        age_window = (user_hash % 3) * 10 + 7  # 7, 17, or 27 days

        for lang in languages:
            try:
                lang_issues = client.search_good_first_issues(
                    languages=[lang],
                    min_stars=20,
                    max_age_days=age_window,
                    limit=15
                )
                all_issues.extend(lang_issues)
            except:
                continue

        # If not enough issues, try with relaxed constraints
        if len(all_issues) < 5:
            try:
                backup_issues = client.search_good_first_issues(
                    languages=languages[:1],
                    min_stars=10,
                    max_age_days=60,
                    limit=20
                )
                all_issues.extend(backup_issues)
            except:
                pass

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

        for issue in unique_issues[:40]:
            score = scorer.score_issue(issue)

            # Vary threshold slightly by user for diversity
            threshold = 0.25 + (user_hash % 10) * 0.01  # 0.25-0.34

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
