# TODO Before Launch

## CRITICAL (Must Do)

### 1. Test Web App ✓ (FIXED)
- [x] Better error handling added
- [x] Demo link added
- [ ] Test with real username on live site
- [ ] Test with invalid username
- [ ] Test with private profile
- [ ] Test on mobile

**Action:** Go to https://good-first-issue.onrender.com and test these scenarios.

### 2. Test CLI Features
- [ ] `gfi find` still works
- [ ] `gfi lucky` works
- [ ] `gfi success` works
- [ ] `gfi telemetry --enable` works
- [ ] Card generation works (check /tmp for PNG)
- [ ] Twitter share prompt works

**Action:** Run these commands locally:
```bash
cd ~/Desktop/good-first-issue
gfi find --lang python
gfi lucky
```

### 3. Verify Render Environment Variable
- [ ] GITHUB_TOKEN is set in Render dashboard
- [ ] Token has correct permissions (public_repo, read:user)
- [ ] Token is not expired

**Action:** Check Render dashboard → Environment → GITHUB_TOKEN

### 4. Add Screenshot to README
- [ ] Take screenshot of CLI output (`gfi find`)
- [ ] Or screenshot of web version with results
- [ ] Add to README between title and features

**How to:**
1. Run `gfi find --lang python`
2. Screenshot the terminal
3. Upload to GitHub repo as `screenshot.png`
4. Add to README: `![Demo](screenshot.png)`

Or use: https://carbon.now.sh for beautiful code screenshots

## HIGH PRIORITY (Should Do)

### 5. Update GitHub Issues
- [ ] Create "good first issue" labels on your repo
- [ ] Create 3-5 actual good first issues
- [ ] Label them properly

**Why:** People will want to contribute. Make it easy.

**Examples:**
- "Add GitLab support"
- "Add tests for card generation"
- "Add watch mode with notifications"
- "Export results to JSON"

### 6. Add Issue Templates
```bash
mkdir -p .github/ISSUE_TEMPLATE
```

Create bug report and feature request templates.

### 7. Test Rate Limits
- [ ] What happens when GitHub API rate limit hits?
- [ ] Does error message make sense?
- [ ] Does app recover?

**Action:** Make 10 quick searches in a row on web version.

## NICE TO HAVE (Can Wait)

### 8. Analytics
Add basic analytics to web version to track:
- Number of searches
- Popular languages
- Success rate

### 9. Tests for New Features
New features (lucky, card, viral, telemetry) have no tests.

### 10. Contributing Guide
Improve CONTRIBUTING.md with:
- Development setup
- Running tests
- Code style
- PR process

### 11. Screenshots for Social Media
Take 3-4 screenshots for:
- Twitter posts
- Product Hunt
- README
- HN comments

### 12. Video Demo (Optional)
30-second screen recording showing:
1. Enter username
2. Results appear
3. Click to view issue

Upload to GitHub, embed in README.

## BEFORE POSTING TO REDDIT

### Final Checklist
- [ ] Web app tested and working
- [ ] CLI tested and working
- [ ] Screenshot added to README
- [ ] Good first issues created on repo
- [ ] Render GITHUB_TOKEN verified
- [ ] Error messages tested
- [ ] Mobile tested
- [ ] Demo link works

## IF SOMETHING BREAKS DURING LAUNCH

### Web App Down
1. Check Render dashboard logs
2. Restart service
3. Check GITHUB_TOKEN is set
4. Post update: "Fixing now, back in 5 min"

### Rate Limit Hit
1. Expected with high traffic
2. Tell users: "High traffic! Back in 1 hour."
3. Consider upgrading GitHub token

### Bug Reported
1. Acknowledge: "Thanks! Looking into it."
2. Fix within 24 hours
3. Reply: "Fixed!"

## CURRENT STATUS

✓ Web app deployed
✓ Error handling improved
✓ Demo link added
⚠ Needs testing
⚠ Needs screenshot

**Next step:** Test the web app thoroughly, then launch.
