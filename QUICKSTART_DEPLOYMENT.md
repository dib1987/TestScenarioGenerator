# 🚀 Quick Deployment Guide for Teams

## Deploy to Cloud in 15 Minutes

Follow these steps to deploy your PR Test Scenario Generator so your entire team can access it from anywhere.

---

## Step 1: Push to GitHub (5 minutes)

### 1.1 Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click "+" → "New repository"
3. Name it: `TestScenarioGenerator`
4. Make it **Public** (or Private if you prefer)
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### 1.2 Push Your Code

Open a new terminal and run:

```bash
cd "c:\Agentic Workflow\TestScenarioGenerator"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - PR Test Scenario Generator"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/TestScenarioGenerator.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Done!** Your code is now on GitHub.

---

## Step 2: Deploy to Render (10 minutes)

### 2.1 Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click "Get Started"
3. Sign up with your GitHub account (easiest)

### 2.2 Create Web Service

1. Click "New +" → "Web Service"
2. Click "Connect account" if needed
3. Find your `TestScenarioGenerator` repository
4. Click "Connect"

### 2.3 Configure Service

Fill in these settings:

**Basic Settings:**
- **Name**: `pr-test-generator` (or your choice)
- **Region**: Choose closest to your team
- **Branch**: `main`
- **Root Directory**: (leave blank)

**Build Settings:**
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- Free (or Starter $7/month for better performance)

### 2.4 Add Environment Variables

**CRITICAL:** Add your API keys!

Click "Advanced" → "Add Environment Variable":

**Variable 1:**
- **Key**: `ANTHROPIC_API_KEY`
- **Value**: Your actual Claude API key from console.anthropic.com

**Variable 2 (Optional):**
- **Key**: `GITHUB_TOKEN`
- **Value**: Your GitHub personal access token

**Variable 3 (Optional):**
- **Key**: `FLASK_DEBUG`
- **Value**: `False`

### 2.5 Deploy!

1. Click "Create Web Service"
2. Wait 2-5 minutes for deployment
3. You'll see build logs in real-time
4. When done, you'll get a URL like: `https://pr-test-generator.onrender.com`

---

## Step 3: Share with Your Team

### Share the Public URL

Once deployed, share this URL with your team:
```
https://your-app-name.onrender.com
```

**Everyone can now:**
- ✅ Access it from anywhere
- ✅ Use it on any device (desktop, mobile, tablet)
- ✅ Analyze GitHub PRs
- ✅ Generate test scenarios
- ✅ No installation needed!

### Team Instructions

Send this to your team:

```
Hi Team!

We now have an AI-powered PR Test Scenario Generator available:

🔗 URL: https://your-app-name.onrender.com

How to use:
1. Open the URL in your browser
2. Paste a GitHub PR URL
3. Click "Generate Test Scenarios"
4. Get comprehensive test scenarios powered by Claude AI!

No installation or setup needed - just use it directly in your browser!
```

---

## Troubleshooting

### Build Failed?
- Check that all files are pushed to GitHub
- Verify `requirements.txt` is in the repository
- Check build logs in Render dashboard

### App Not Loading?
- Check environment variables are set correctly
- Verify `ANTHROPIC_API_KEY` is valid
- Check logs in Render dashboard

### API Errors?
- Verify Anthropic API key has credits
- Check API key permissions at console.anthropic.com

---

## Updating the App

To update after making changes:

```bash
cd "c:\Agentic Workflow\TestScenarioGenerator"

# Make your changes, then:
git add .
git commit -m "Description of changes"
git push origin main
```

**Render will automatically re-deploy!** (if auto-deploy is enabled)

---

## Cost Considerations

### Free Tier (Render)
- ✅ 750 hours/month free
- ⚠️ Sleeps after 15 minutes of inactivity
- ⚠️ First request after sleep takes ~30 seconds
- ✅ Perfect for testing and small teams

### Paid Tier ($7/month)
- ✅ Always on (no sleep)
- ✅ Faster performance
- ✅ Better for active teams
- ✅ 99.9% uptime

### API Costs (Anthropic)
- Claude Sonnet: ~$3 per million tokens
- Typical analysis: ~2000-5000 tokens
- Budget: $5-20/month for moderate team use

---

## Security Best Practices

1. ✅ Never commit `.env` file (already in .gitignore)
2. ✅ Use environment variables for secrets
3. ✅ Set `FLASK_DEBUG=False` in production
4. ✅ Keep dependencies updated
5. ✅ Monitor API usage

---

## Next Steps

After deployment:
- [ ] Test the deployed URL
- [ ] Share with team
- [ ] Set up custom domain (optional)
- [ ] Enable monitoring/alerts
- [ ] Set up budget alerts for API usage

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions or create an issue on GitHub.
