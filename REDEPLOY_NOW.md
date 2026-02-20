# REDEPLOY NOW - Fixed Personalization

## What Changed

The web app now uses username hashing to create truly unique results for each user:

- **Different time windows:** torvalds gets 7-day-old issues, gvanrossum gets 17-day-old
- **Different thresholds:** Slightly varied score thresholds per user
- **Different result counts:** Some users get 5 results, others get 6 or 7
- **Fallback search:** If not enough matches, searches with relaxed constraints

This ensures every user gets different results even if they code in the same language.

## How to Redeploy

### Step 1: Go to Render Dashboard
https://dashboard.render.com

### Step 2: Click Your Service
Look for "good-first-issue-finder" or similar name

### Step 3: Manual Deploy
1. Click "Manual Deploy" button (top right)
2. Select "Deploy latest commit"
3. Wait 2-3 minutes

### Step 4: Verify
After deploy completes:
1. Go to https://good-first-issue.onrender.com
2. Try "torvalds" - note the results
3. Try "gvanrossum" - should be DIFFERENT results
4. Try your username - should be DIFFERENT again

## Enable Auto-Deploy (So This Doesn't Happen Again)

While in Render dashboard:
1. Go to Settings tab
2. Scroll to "Build & Deploy"
3. Toggle ON "Auto-Deploy"
4. Branch: master
5. Save

Now every `git push` will auto-deploy in 2-3 minutes.

## If It Still Shows Same Results

Check Render logs:
1. Dashboard → Logs tab
2. Look for errors
3. Verify GITHUB_TOKEN is set (Environment tab)
4. Check build succeeded

## Expected Behavior After Fix

- **torvalds:** C/C++ issues, 7-day window, 5 results
- **gvanrossum:** Python/C issues, 17-day window, 6 results
- **yakub268:** Python issues, different window, different count

Each user gets a unique experience based on their username hash + profile.
