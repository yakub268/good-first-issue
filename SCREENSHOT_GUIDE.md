# Screenshot Guide for README

## Quick Screenshots Needed (5 minutes)

### 1. CLI Output
Run this and screenshot:
```bash
gfi find --lang python --limit 5
```

**What to capture:** The beautiful table output with scores, repos, and issues.

**Where to add:** After the "Why This Exists" section in README.md

### 2. Web Version
Go to: https://good-first-issue.onrender.com
- Enter "torvalds"
- Wait for results
- Screenshot the results

**What to capture:** The clean web UI with issue cards.

### 3. Lucky Mode (Optional)
```bash
gfi lucky --lang python
```

**What to capture:** The detailed single-issue view with score breakdown.

## How to Add to README

1. Take screenshots and save as:
   - `demo-cli.png`
   - `demo-web.png`
   - `demo-lucky.png` (optional)

2. Upload to GitHub repo root

3. Add to README.md after line 16:
```markdown
## Demo

### CLI
![CLI Demo](demo-cli.png)

### Web Version
Try it live: https://good-first-issue.onrender.com

![Web Demo](demo-web.png)
```

## Alternative: Use Carbon for Code Screenshots

For beautiful terminal screenshots:
1. Go to https://carbon.now.sh
2. Paste CLI output
3. Choose theme: "Monokai" or "Night Owl"
4. Export PNG
5. Add to README

## GIF (Optional but Great for Shares)

Use https://www.screentogif.com/ or macOS QuickTime to record:
1. Open terminal
2. Type `gfi find --lang python`
3. Watch results appear
4. 5-10 seconds total
5. Save as `demo.gif`

Add to README:
```markdown
![Demo](demo.gif)
```

This is VERY shareable on Twitter/HN.
