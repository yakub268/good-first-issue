# Deploy Web Version - Quick Guide

Your browser should have opened to Render.com. Follow these steps:

## Step 1: Connect GitHub (if not already)
1. Click "Connect GitHub" or sign in with GitHub
2. Authorize Render to access your repositories

## Step 2: Select Repository
1. Find "yakub268/good-first-issue" in the list
2. Click "Connect"

## Step 3: Configure Service
Fill in these settings:

**Name:** `good-first-issue-finder` (or anything you want)

**Region:** Oregon (US West) - closest to most users

**Branch:** `master`

**Root Directory:** `web`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app
```

**Plan:** Free

## Step 4: Add Environment Variable
Click "Advanced" and add:

**Key:** `GITHUB_TOKEN`
**Value:** `ghp_your_github_token_here`

(Get a token at https://github.com/settings/tokens if you don't have one)

## Step 5: Deploy
1. Click "Create Web Service"
2. Wait 2-3 minutes for build
3. Your site will be live at: `https://good-first-issue-finder.onrender.com`

## Alternative: Railway (Even Easier)

If Render doesn't work:

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose "yakub268/good-first-issue"
5. Railway auto-detects Python
6. Set root directory: `web`
7. Add env var: `GITHUB_TOKEN=ghp_your_token`
8. Deploy
9. Live at: `https://your-app.railway.app`

## Alternative: Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd ~/Desktop/good-first-issue/web
vercel
```

3. Follow prompts
4. Add GITHUB_TOKEN in Vercel dashboard

## After Deployment

1. Test the live URL
2. Update your Reddit/HN posts with the live link
3. Add URL to README.md
4. Share on Twitter with live demo link

## Custom Domain (Optional)

After deployment, you can add a custom domain:
- Buy domain from Namecheap/Porkbun ($10/year)
- Add domain in Render/Railway dashboard
- Update DNS records
- SSL auto-configured

Example: `gfi-finder.dev` or `goodfirstissue.app`
