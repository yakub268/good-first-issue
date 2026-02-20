# New Features Added (Feb 20, 2026)

## 1. Export to JSON/CSV
**Command:** `gfi find --export json` or `gfi find --export csv`

Export your search results to a file for further processing.

**JSON output includes:**
- All scores (total, clarity, maintainer, freshness, activity)
- Issue details (title, URL, repo, language, stars)
- Timestamps, labels, comments
- Score breakdown and reason

**CSV output includes:**
- All key metrics in spreadsheet format
- Easy to analyze in Excel/Google Sheets

**Example:**
```bash
gfi find --lang python --export json
# Creates: gfi_results_username_20260220_153045.json

gfi find --lang rust --export csv
# Creates: gfi_results_username_20260220_153122.csv
```

## 2. Watch Mode Daemon
**Commands:**
- `gfi watch --start` - Start background daemon
- `gfi watch --stop` - Stop daemon
- `gfi watch --status` - Check status

Runs in background, checks every 6 hours for new good first issues, sends desktop notifications when excellent matches found (score ≥ 0.7).

**Features:**
- Tracks seen issues (no duplicate notifications)
- Desktop notifications (macOS, Windows, Linux)
- Configurable check interval
- Only notifies for high-quality matches

**Example:**
```bash
# Start watching
gfi watch --start

# You'll get notifications like:
# "New Good First Issue (0.87)"
# "Add migration helper for common patterns"
# "django/django"

# Check status
gfi watch --status

# Stop watching
gfi watch --stop
```

**Installation for notifications:**
```bash
pip install good-first-issue[watch]
```

## 3. Social Meta Tags
Web version now has proper OpenGraph and Twitter Card meta tags.

**Benefits:**
- Beautiful previews when sharing on Twitter/LinkedIn
- Proper title, description, and image
- Better SEO

**Try it:** Share https://good-first-issue.onrender.com on Twitter/LinkedIn and see the preview.

## 4. Improved Error Handling
Web app now handles:
- User not found (404 with clear message)
- Private profiles
- Empty profiles (no repos)
- API failures (graceful degradation)

## Summary

**Before:** CLI tool with basic search
**After:** Full-featured platform with export, watch mode, and professional web presence

**Total new code:** ~350 lines
**New files:** 2 (export.py, watch.py)
**Commands added:** 2 (watch, export flag)

Ready for launch!
