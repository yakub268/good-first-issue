# 🎯 Good First Issue Finder

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/yakub268/good-first-issue?style=social)](https://github.com/yakub268/good-first-issue)

Find "good first issue" labeled issues in open source projects you'll actually want to contribute to.

## Why This Exists

Most "good first issue" finders just dump a list of random issues. This tool:

- **Analyzes your GitHub profile** to understand what you care about
- **Scores issues** based on clarity, maintainer responsiveness, and project health
- **Filters noise** — no vague issues, no dead projects, no overwhelmed maintainers
- **Shows what matters** — clear descriptions, realistic scope, active engagement

## Features

- 🔍 **Smart search** — finds issues in your preferred languages from your starred repos
- 📊 **Multi-factor scoring** — clarity, maintainer response time, freshness, project activity
- 🎨 **Beautiful terminal UI** — powered by Rich
- ⚡ **Fast** — persistent HTTP connections, smart caching
- 🔒 **Private** — your token stays local, no external tracking

## Installation

```bash
cd good-first-issue
python -m venv venv
venv\Scripts\activate  # Windows
pip install -e .
```

## Quick Start

1. **Get a GitHub token** (required for API access):
   - Go to https://github.com/settings/tokens
   - Create a classic token with `public_repo` and `read:user` scopes
   - Copy the token

2. **Initialize**:
   ```bash
   gfi init --token ghp_your_token_here
   ```

   Or set environment variable:
   ```bash
   # .env file
   GITHUB_TOKEN=ghp_your_token_here

   gfi init
   ```

3. **Find issues**:
   ```bash
   gfi find
   ```

## Usage

### Find issues matching your profile
```bash
gfi find
```

### Filter by specific languages
```bash
gfi find --lang python --lang rust
```

### Adjust filters
```bash
gfi find --min-stars 100 --max-age 14 --limit 20
```

### View issue details
```bash
gfi show https://github.com/owner/repo/issues/123
```

## How It Works

### Profile Analysis
When you run `gfi init`, it:
- Analyzes your starred repositories
- Extracts your most-used languages
- Identifies topics you're interested in
- Counts your contribution activity

### Issue Scoring
Each issue gets scored (0-1) across four dimensions:

**Clarity (35% weight)**
- Has detailed description (>100 chars)
- Includes acceptance criteria or reproduction steps
- Contains code examples
- Not overwhelming (<2000 chars)

**Maintainer Responsiveness (30% weight)**
- Average time to close recent issues
- Response patterns on similar issues
- Project engagement signals

**Freshness (20% weight)**
- Sweet spot: 1-30 days old
- Not too fresh (might be unclear)
- Not too stale (might be abandoned)

**Project Activity (15% weight)**
- Repository stars (popularity)
- Recent updates
- Healthy discussion (1-5 comments ideal)

## Example Output

```
🎯 Good First Issues For You
┌───────┬────────────────────────┬───────────────────────────┬────────┬───────┐
│ Score │ Project                │ Issue                     │ Lang   │ Stars │
├───────┼────────────────────────┼───────────────────────────┼────────┼───────┤
│  0.80 │ jatinkrmalik/vocalinux │ 📰 Help Wanted: Create    │ Python │    97 │
│       │                        │ Wikipedia Page for Voc... │        │       │
│  0.68 │ NOVUS-X/StellArts      │ 🟠 LOW — Contracts CI     │ Python │     1 │
│       │                        │ Missing `cargo clippy`    │        │       │
│       │                        │ ...                       │        │       │
│  0.57 │ chatvector-ai/chatv... │ Create Interactive Star   │ Python │    11 │
│       │                        │ Progress Bar in README    │        │       │
└───────┴────────────────────────┴───────────────────────────┴────────┴───────┘

Showing top 3 issues
Run 'gfi show <url>' for details
```

## Configuration

Config stored in `~/.gfi-config.json`:
```json
{
  "token": "ghp_...",
  "username": "yourname",
  "languages": ["Python", "JavaScript", "Rust"],
  "interests": ["machine-learning", "cli", "web"]
}
```

## Contributing

This project itself has good first issues! Check the Issues tab.

## License

MIT License - see LICENSE file
