# Good First Issue Finder

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/yakub268/good-first-issue?style=social)](https://github.com/yakub268/good-first-issue)

Find "good first issue" labeled issues in open source projects you'll actually want to contribute to.

**[Try it instantly (no install)](https://good-first-issue.onrender.com)** | [Install CLI](#installation)

## Why This Exists

Most "good first issue" finders just dump a list of random issues. This tool:

- **Analyzes your GitHub profile** to understand what you care about
- **Scores issues** based on clarity, maintainer responsiveness, and project health
- **Filters noise** — no vague issues, no dead projects, no overwhelmed maintainers
- **Shows what matters** — clear descriptions, realistic scope, active engagement

## Demo

### CLI Output
![CLI Demo](docs/screenshots/demo-cli.svg)

### Initialization
![Init Success](docs/screenshots/demo-init.svg)

### Detailed Issue View
![Issue Detail](docs/screenshots/demo-show.svg)

## Features

- **Smart search** — finds issues in your preferred languages from your starred repos
- **Multi-factor scoring** — clarity, maintainer response time, freshness, project activity
- **Beautiful terminal UI** — powered by Rich
- **Shareable result cards** — auto-generated PNGs perfect for Twitter/LinkedIn
- **Lucky mode** — get ONE perfect match instantly
- **Web version** — [try it instantly](https://good-first-issue.onrender.com) without installing
- **Success tracking** — track your contributions and celebrate wins
- **GraphQL API** — optional GraphQL support for 3x faster searches and better rate limits
- **Export results** — save to JSON or CSV for analysis and tracking
- **Fast** — persistent HTTP connections, smart caching
- **Private** — your token stays local, optional anonymous telemetry

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

### Get ONE perfect match (lucky mode)
```bash
gfi lucky
```

### Filter by specific languages
```bash
gfi find --lang python --lang rust
```

### Search alternative labels
```bash
# Search for "help wanted" and "beginner friendly" labels
gfi find --labels "help wanted" --labels "beginner friendly"

# Default: searches "good first issue", "help wanted", and "beginner friendly"
gfi find
```

### Search on GitLab
```bash
# Search GitLab instead of GitHub
gfi find --platform gitlab

# Works with all other options
gfi find --platform gitlab --lang python --min-stars 100
```

### Use GraphQL for better performance
```bash
# Use GitHub's GraphQL API (faster, fewer rate limits)
gfi find --use-graphql

# Works with all find options
gfi find --use-graphql --lang python --min-stars 100

# Also works with lucky mode
gfi lucky --use-graphql
```

### Export results
```bash
# Export to JSON
gfi find --export json

# Export to CSV
gfi find --export csv
```

### Adjust filters
```bash
gfi find --min-stars 100 --max-age 14 --limit 20
```

### View issue details
```bash
gfi show https://github.com/owner/repo/issues/123
```

### Track your successes
```bash
gfi success https://github.com/owner/repo/issues/123 --pr https://github.com/owner/repo/pull/456
gfi wins
```

### Watch for new issues (daemon)
```bash
# Start background daemon (checks every 6 hours)
gfi watch --start

# Check status
gfi watch --status

# Stop daemon
gfi watch --stop
```

Desktop notifications for high-quality issues (score ≥ 0.7)

### Enable live stats (optional)
```bash
gfi telemetry --enable
gfi stats
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

## Roadmap

- [x] Shareable result cards
- [x] Lucky mode (one perfect match)
- [x] Web version (instant, no install)
- [x] Success tracking
- [x] Live activity stats
- [x] Support for GitLab issues
- [x] Alternative labels ("help wanted", "beginner friendly")
- [x] Watch mode with notifications (daemon)
- [x] Export results to JSON/CSV
- [x] GraphQL API support for better performance

See [open issues](https://github.com/yakub268/good-first-issue/issues) for more.

## Contributing

This project itself has good first issues! Check the [Issues tab](https://github.com/yakub268/good-first-issue/issues).

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Star History

If you find this useful, consider giving it a star! ⭐

## Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - Beautiful CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [httpx](https://www.python-httpx.org/) - Modern HTTP client
- [Pydantic](https://docs.pydantic.dev/) - Data validation

Inspired by the need for better discovery in the open source ecosystem.

## License

MIT License - see [LICENSE](LICENSE) file

---

Made with ❤️ for the open source community. Happy contributing!
