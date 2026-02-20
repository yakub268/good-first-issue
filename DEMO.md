# Quick Demo

## Setup (30 seconds)

1. **Get GitHub token**:
   - Visit https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `public_repo`, `read:user`
   - Copy token

2. **Install & Initialize**:
   ```bash
   cd good-first-issue
   python -m venv venv
   venv\Scripts\activate
   pip install -e .

   # Set token
   gfi init --token ghp_YOUR_TOKEN
   ```

## Usage

### Find issues matching your profile
```bash
gfi find
```

Output:
```
┌─────────────────────── 🎯 Good First Issues For You ───────────────────────┐
│ Score  Project                    Issue                              Lang       ⭐ │
├──────────────────────────────────────────────────────────────────────────────────┤
│  0.87  django/django              Add database migration helper      Python     75k │
│  0.82  psf/requests               Improve SSL error messages         Python     51k │
│  0.78  pallets/flask              Add type hints to decorators       Python     66k │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Filter by language
```bash
gfi find --lang rust --lang go
```

### Adjust criteria
```bash
gfi find --min-stars 1000 --max-age 7 --limit 5
```

### View details
```bash
gfi show https://github.com/owner/repo/issues/123
```

Shows:
- Score breakdown (clarity, maintainer response, freshness, activity)
- Full issue description
- Project metadata
- Quick assessment

## What Makes a Good Score?

**0.8-1.0** (Excellent)
- Clear description with acceptance criteria
- Active maintainers (respond within 7 days)
- Posted recently (1-7 days)
- Popular, healthy project

**0.6-0.8** (Good)
- Decent description
- Responsive maintainers (respond within 30 days)
- Posted within last month
- Active project

**0.3-0.6** (Okay)
- Basic description
- Slow maintainer response
- Older issue or less active project

**<0.3** (Filtered out)
- Vague or missing description
- Abandoned project
- Very old or brand new issue

## Tips

1. **Start with defaults** — `gfi find` uses your profile automatically
2. **Lower stars for more options** — `--min-stars 10` finds smaller projects
3. **Bookmark good ones** — copy URLs to a file for later
4. **Check maintainer response** — high scores mean they'll likely review your PR
5. **Read the description** — even high-scoring issues may not match your skills

## What's Next?

- Click the issue URL
- Read full context
- Comment "I'd like to work on this"
- Fork, branch, code, PR!

Good luck with your first contribution! 🚀
