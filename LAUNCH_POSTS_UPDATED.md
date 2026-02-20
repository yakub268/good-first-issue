# Updated Launch Posts - With Live Demo

Now that the web version is live at https://good-first-issue.onrender.com, here are updated posts.

---

## Reddit r/Python (UPDATED)

**Title:**
```
I built a CLI tool to find good first issues in projects you actually care about
```

**Post Body:**
```
After weeks of trying to find my first open source contribution, I got frustrated. Every "good first issue" finder I tried just dumped random issues - half were vague, a quarter were in dead projects, and none matched my interests.

So I built **Good First Issue Finder** - a CLI that actually works.

**What My Project Does**

Good First Issue Finder analyzes your GitHub profile (starred repos, languages, contribution history) and uses that to find personalized "good first issue" matches. Each issue gets scored 0-1 across four factors:

- Clarity (35%): Has clear description, acceptance criteria, code examples
- Maintainer Response (30%): How fast they close/respond to issues
- Freshness (20%): Sweet spot is 1-30 days old
- Project Activity (15%): Stars, recent updates, healthy discussion

Only shows issues scoring above 0.3. Issues scoring 0.7+ are usually excellent.

**Target Audience**

This is for developers looking to make their first (or next) open source contribution. It's production-ready - fully tested, handles GitHub API rate limits, persistent HTTP connections, smart caching. MIT licensed, ready to use today.

**Comparison**

Most "good first issue" finders (goodfirstissue.dev, firstissue.dev, etc.) just query GitHub's label and dump results. No personalization, no quality filtering, no scoring. You get random projects you've never heard of with vague issues like "improve docs."

This tool is different because it:
- Personalizes to YOUR interests by analyzing your GitHub activity
- Scores every issue on multiple quality dimensions
- Filters out noise (dead projects, overwhelmed maintainers, unclear issues)
- Shows you WHY each issue scored the way it did

**Try it instantly (no install required):**
https://good-first-issue.onrender.com

Or install the CLI:
```bash
pip install git+https://github.com/yakub268/good-first-issue
gfi init --token YOUR_GITHUB_TOKEN
gfi find --lang python
```

**Tech stack:**
Python 3.10+, Click, Rich, httpx, Pydantic, GitHub REST API. 826 lines of code.

**GitHub:** https://github.com/yakub268/good-first-issue

The project itself has good first issues if you want to contribute! Questions welcome - this is my first real OSS project.
```

---

## Hacker News (Show HN)

**Title:**
```
Show HN: Good First Issue Finder - Try it instantly, no install required
```

**URL:**
```
https://good-first-issue.onrender.com
```

**First Comment (post IMMEDIATELY after submitting):**
```
Author here. After weeks of failing to find my first OSS contribution, I built this.

The problem: Every "good first issue" finder dumps random issues. Half are vague ("improve docs"), a quarter are in dead projects, none match your interests.

Try it now (no install): https://good-first-issue.onrender.com
Enter your GitHub username and see personalized matches in 5 seconds.

How it works:
- Analyzes your GitHub profile (starred repos, languages)
- Scores issues on 4 factors: clarity (35%), maintainer response (30%), freshness (20%), activity (15%)
- Only shows issues in projects you care about

For power users, there's a CLI:
  pip install git+https://github.com/yakub268/good-first-issue
  gfi init --token YOUR_GITHUB_TOKEN
  gfi find --lang python

CLI adds: shareable result cards, success tracking, lucky mode (one perfect match).

Tech: Python CLI using GitHub API, Rich for UI, Click for commands. 826 LOC, MIT licensed. Flask web version deployed on Render.

The project itself has good first issues for contributors. Happy to answer questions!
```

---

## Twitter/X (Thread)

**Tweet 1:**
```
Spent weeks trying to find my first open source contribution. Every tool I tried was useless.

So I built one that actually works.

Try it (no install): https://good-first-issue.onrender.com

Just enter your GitHub username.
```

**Tweet 2 (30 min later):**
```
Here's what makes it different:

Most finders dump random issues. This one:
- Analyzes YOUR GitHub profile
- Scores issues on clarity, maintainer response, project health
- Only shows matches you'd care about

Found a 0.89-scored Django issue in 10 seconds.
```

**Tweet 3 (2 hours later with screenshot):**
```
The web version is instant. The CLI has power features:

- gfi lucky (one perfect match)
- Auto-generated shareable cards
- Success tracking
- Live stats

GitHub: https://github.com/yakub268/good-first-issue

Open source, MIT licensed, 826 LOC.
```

---

## LinkedIn

**Post:**
```
I built a tool to solve a problem every new contributor faces: finding that first open source issue.

Try it instantly (no install): https://good-first-issue.onrender.com

Most "good first issue" lists are noise. This tool:
- Analyzes your GitHub activity
- Scores issues on 4 quality factors
- Shows only projects you'd care about

Built with Python, Click, Rich. MIT licensed. 826 lines of code.

Also available as a CLI with advanced features (shareable cards, success tracking, lucky mode):
GitHub: https://github.com/yakub268/good-first-issue

The project itself has good first issues if you want to contribute!

#OpenSource #Python #DeveloperTools #GitHub
```

---

## Dev.to

**Add this section at the top:**

```markdown
## Try It Now

Don't want to install anything? Try the web version:
**https://good-first-issue.onrender.com**

Enter your GitHub username and get results in 5 seconds.

For power users, continue reading for the CLI version.
```

---

## Product Hunt

**First line of description:**
```
Try it instantly at https://good-first-issue.onrender.com - no install, no signup, works in 5 seconds.

[rest of description...]
```

---

## Key Changes

1. **Lead with the live link** - removes all friction
2. **"Try it instantly"** - emphasizes zero-install
3. **Mention both versions** - web for quick try, CLI for power users
4. **Add call-to-action** - "Enter your GitHub username"

## Note on Render Free Tier

The site may take 10-20 seconds to wake up on first visit (cold start). After that it's fast. Mention this if people ask about slowness:

> "Running on Render's free tier - first load takes ~15 seconds (cold start), then it's instant. Upgrade to paid tier removes this."

## Launch Order

1. **Post to Reddit r/Python first** - highest engagement
2. **Wait 2 hours, then Hacker News** - different audience
3. **Twitter thread** - throughout the day
4. **LinkedIn** - next day
5. **Dev.to article** - 2-3 days later
6. **Product Hunt** - wait 1 week for traction

## Important

When you post on HN, **post the first comment within 60 seconds** or your submission may be flagged. Have it ready to copy-paste.
