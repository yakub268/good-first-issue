# Reddit Post for r/Python

## Title
I built a CLI tool to find good first issues in projects you actually care about

## Post Body

After weeks of trying to find my first open source contribution, I got frustrated. Every "good first issue" finder I tried just dumped random issues - half were vague, a quarter were in dead projects, and none matched my interests.

So I built **Good First Issue Finder** - a CLI that actually works:

## What it does:
- 🔍 Analyzes YOUR GitHub profile (starred repos, languages you use)
- 📊 Scores issues on 4 quality factors:
  - **Clarity** (35%): Has clear description, acceptance criteria, code examples
  - **Maintainer Response** (30%): How fast they close/respond to issues
  - **Freshness** (20%): Sweet spot is 1-30 days old
  - **Project Activity** (15%): Stars, recent updates, healthy discussion
- 🎯 Only shows issues in projects you'd actually care about
- 🎨 Beautiful terminal UI powered by Rich

## Quick example:
```bash
pip install git+https://github.com/yakub268/good-first-issue
gfi init --token YOUR_GITHUB_TOKEN
gfi find --lang python
```

Output:
```
🎯 Good First Issues For You
┌───────┬────────────────────────┬───────────────────────────┬────────┬───────┐
│ Score │ Project                │ Issue                     │ Lang   │ Stars │
├───────┼────────────────────────┼───────────────────────────┼────────┼───────┤
│  0.80 │ jatinkrmalik/vocalinux │ 📰 Help Wanted: Create    │ Python │    97 │
│       │                        │ Wikipedia Page for Voc... │        │       │
│  0.68 │ NOVUS-X/StellArts      │ 🟠 LOW — Contracts CI     │ Python │     1 │
│       │                        │ Missing `cargo clippy`    │        │       │
└───────┴────────────────────────┴───────────────────────────┴────────┴───────┘
```

Then use `gfi show <url>` to see detailed score breakdown before you commit.

## Tech stack:
- Python 3.10+
- Click (CLI), Rich (terminal UI), httpx (HTTP client), Pydantic (validation)
- GitHub REST API
- 826 lines of code, fully tested with real data

## GitHub: https://github.com/yakub268/good-first-issue

The project itself has good first issues if you want to contribute! I'm actively responding to PRs and feedback.

**Questions/ideas welcome!** This is my first real OSS project and I'd love to hear what you think.

---

## Flair
Project

## Tags
[Project] [CLI] [GitHub]
