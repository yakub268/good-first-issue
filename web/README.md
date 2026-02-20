# Web Version - Good First Issue Finder

Instant web interface for finding good first issues.

## Quick Start

1. Set your GitHub token:
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

2. Run the server:
```bash
cd web
python app.py
```

3. Open browser to http://localhost:5001

## Deploy to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd web
vercel
```

3. Set environment variable in Vercel dashboard:
- GITHUB_TOKEN=your_token

## Features

- Zero install required for users
- Instant results in browser
- Works on mobile
- Clean, modern UI
- No signup required

## Rate Limits

The web version uses a shared GitHub token and is subject to GitHub API rate limits (5000 requests/hour). For unlimited usage, install the CLI with your own token.
