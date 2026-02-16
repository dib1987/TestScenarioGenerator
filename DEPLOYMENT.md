# 🚀 Deployment Guide

Complete guide to deploying the PR Test Scenario Generator to various cloud platforms.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Deploy to Render](#deploy-to-render-recommended)
- [Deploy to Heroku](#deploy-to-heroku)
- [Deploy to Railway](#deploy-to-railway)
- [Deploy to AWS/Azure/GCP](#deploy-to-other-platforms)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

1. **GitHub Account** - To host your repository
2. **Anthropic API Key** - Get from [console.anthropic.com](https://console.anthropic.com/)
3. **GitHub Token** (Optional) - For analyzing private repositories
4. **Git** installed locally
5. **Cloud Platform Account** - Choose one:
   - [Render](https://render.com) - Recommended, free tier available
   - [Heroku](https://heroku.com) - Popular, paid tiers
   - [Railway](https://railway.app) - Easy deployment
   - AWS, Azure, GCP - Enterprise solutions

---

## Environment Variables

Your deployment will need these environment variables:

### Required
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx    # Your Claude AI API key
```

### Optional
```env
GITHUB_TOKEN=ghp_xxxxx            # For private repo access
PORT=5000                          # Port (usually auto-set by platform)
FLASK_DEBUG=False                  # Set to False in production
FLASK_SECRET_KEY=your-secret-key   # Random string for sessions
```

---

## Deploy to Render (Recommended)

### Why Render?
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Custom domains
- ✅ SSL certificates included
- ✅ Easy environment variable management

### Step-by-Step Deployment

1. **Push Code to GitHub**
   ```bash
   cd "c:\Agentic Workflow\TestScenarioGenerator"

   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit - PR Test Scenario Generator"

   # Create GitHub repo and push
   # (Create repo on github.com first, then:)
   git remote add origin https://github.com/yourusername/TestScenarioGenerator.git
   git branch -M main
   git push -u origin main
   ```

2. **Sign Up for Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (recommended)

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Click "Connect account" if needed
   - Select your repository
   - Click "Connect"

4. **Configure Service**
   - **Name**: `pr-test-generator` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. **Advanced Settings**
   - **Auto-Deploy**: Yes (recommended)
   - **Instance Type**: Free (or paid for better performance)

6. **Add Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   - Add these:
     ```
     Key: ANTHROPIC_API_KEY
     Value: your_actual_api_key_here

     Key: GITHUB_TOKEN
     Value: your_github_token_here

     Key: FLASK_DEBUG
     Value: False
     ```

7. **Deploy!**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Your app will be live at: `https://pr-test-generator.onrender.com`

### Auto-Deployments
Every push to `main` branch will automatically trigger a new deployment!

---

## Deploy to Heroku

### Prerequisites
- Heroku account
- Heroku CLI installed

### Installation (Heroku CLI)

**Windows (PowerShell as Administrator):**
```powershell
# Using Chocolatey
choco install heroku-cli

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

**macOS:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Deployment Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   cd "c:\Agentic Workflow\TestScenarioGenerator"
   heroku create your-app-name
   # Example: heroku create pr-test-gen-2024
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_actual_key_here
   heroku config:set GITHUB_TOKEN=your_github_token_here
   heroku config:set FLASK_DEBUG=False
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Open Your App**
   ```bash
   heroku open
   ```

### View Logs
```bash
heroku logs --tail
```

### Scale Dynos (if needed)
```bash
heroku ps:scale web=1
```

---

## Deploy to Railway

Railway offers the simplest deployment process!

### Steps

1. **Visit [railway.app](https://railway.app)**

2. **Sign Up/Login** with GitHub

3. **Create New Project**
   - Click "New Project"
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python!

4. **Add Environment Variables**
   - Click on your project
   - Go to "Variables" tab
   - Add:
     - `ANTHROPIC_API_KEY`
     - `GITHUB_TOKEN`
     - `FLASK_DEBUG` = `False`

5. **Deploy**
   - Railway automatically deploys!
   - Get your URL from the "Settings" tab

### Custom Domain (Optional)
- Go to Settings → Domains
- Add your custom domain
- Update DNS records as instructed

---

## Deploy to Other Platforms

### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize**
   ```bash
   eb init -p python-3.11 pr-test-generator
   ```

3. **Create Environment**
   ```bash
   eb create pr-test-env
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv ANTHROPIC_API_KEY=your_key_here GITHUB_TOKEN=your_token_here
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

### Google Cloud Platform (App Engine)

1. **Create `app.yaml`**
   ```yaml
   runtime: python311
   entrypoint: gunicorn -b :$PORT app:app

   env_variables:
     ANTHROPIC_API_KEY: "your_key_here"
     GITHUB_TOKEN: "your_token_here"
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

### Azure Web Apps

1. **Create Web App**
   ```bash
   az webapp up --name pr-test-generator --runtime PYTHON:3.11
   ```

2. **Set Environment Variables**
   ```bash
   az webapp config appsettings set --name pr-test-generator \
     --settings ANTHROPIC_API_KEY=your_key_here GITHUB_TOKEN=your_token_here
   ```

---

## Post-Deployment

### 1. Test Your Deployment

Visit your app URL and test:
- ✅ Homepage loads
- ✅ Can analyze a public GitHub PR
- ✅ Test scenarios generate successfully
- ✅ Download functionality works

### 2. Set Up Custom Domain (Optional)

**Render:**
- Settings → Custom Domains → Add Domain

**Heroku:**
```bash
heroku domains:add www.yourdomain.com
```

**Railway:**
- Settings → Domains → Add Custom Domain

### 3. Enable HTTPS
Most platforms (Render, Heroku, Railway) provide free SSL certificates automatically!

### 4. Set Up Monitoring

**Render:** Built-in metrics and logs

**Heroku:**
```bash
heroku addons:create papertrail
heroku logs --tail
```

**Railway:** Built-in logging in dashboard

### 5. Configure Auto-Scaling (Optional)

For high traffic, enable auto-scaling in your platform's settings.

---

## Troubleshooting

### Application Won't Start

**Check logs:**
```bash
# Render: View in dashboard
# Heroku:
heroku logs --tail

# Railway: View in dashboard
```

**Common issues:**
- Missing environment variables
- Wrong start command in Procfile
- Dependency installation failed

### "Application Error" Page

1. Check environment variables are set
2. Verify Procfile exists and is correct
3. Check Python version in runtime.txt
4. View platform logs for details

### API Key Errors

- Verify `ANTHROPIC_API_KEY` is set correctly
- No quotes or extra spaces in the value
- Key has sufficient credits at console.anthropic.com

### GitHub Token Issues

- Check token has `repo` or `public_repo` scope
- Token not expired
- For private repos, ensure `GITHUB_TOKEN` is set

### Slow Performance

**Free tiers** may have:
- Slower response times
- Cold starts (first request after inactivity)

**Solutions:**
- Upgrade to paid tier
- Use keep-alive service (for Render free tier)
- Optimize code and reduce dependencies

### Database/State Issues

This app is stateless, but if you add database:
- Use platform-provided databases
- Store connection string in environment variables

---

## Performance Optimization

### 1. Use Production WSGI Server
Already configured with Gunicorn in Procfile ✅

### 2. Enable Caching
Add Redis for caching Claude AI responses:
```bash
# Heroku
heroku addons:create heroku-redis:mini

# Render
# Add Redis instance in dashboard
```

### 3. Optimize Worker Count
```
web: gunicorn app:app --workers 4 --timeout 120
```

### 4. Enable Compression
Flask-Compress (add to requirements.txt):
```python
from flask_compress import Compress
Compress(app)
```

---

## Security Best Practices

1. **Never commit `.env` file** - Already in .gitignore ✅
2. **Use environment variables** - Already configured ✅
3. **Set `FLASK_DEBUG=False`** in production
4. **Use strong `FLASK_SECRET_KEY`**
5. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

---

## Updating Your Deployment

### Auto-Deploy (Recommended)

**Render/Railway/Heroku with GitHub:**
Just push to main branch:
```bash
git add .
git commit -m "Update feature"
git push origin main
```
Deployment happens automatically!

### Manual Deploy

**Heroku:**
```bash
git push heroku main
```

**Render/Railway:**
Click "Manual Deploy" in dashboard

---

## Cost Estimation

### Free Tiers

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| **Render** | 750 hours/month | Sleeps after 15min inactivity |
| **Railway** | $5 free credit/month | Pay for usage beyond |
| **Heroku** | Eco dynos $5/month | Must pay for any dyno |

### Paid Tiers (Monthly)

| Platform | Starting Price | Features |
|----------|----------------|----------|
| **Render** | $7/month | Always-on, better performance |
| **Heroku** | $7/month | Basic dyno, always-on |
| **Railway** | Usage-based | Pay for what you use |

### API Costs

- **Anthropic Claude API**: Pay per token
  - Sonnet: ~$3 per million tokens
  - Haiku: Cheaper option
- Budget: ~$5-20/month for moderate usage

---

## Support

### Platform-Specific Help

- **Render**: [render.com/docs](https://render.com/docs)
- **Heroku**: [devcenter.heroku.com](https://devcenter.heroku.com/)
- **Railway**: [docs.railway.app](https://docs.railway.app/)

### Application Issues

- Check application logs
- Review environment variables
- Test locally first: `python app.py`
- Open GitHub issue for bugs

---

## Next Steps

After deployment:

1. ✅ Test thoroughly with different PR URLs
2. ✅ Share with your team
3. ✅ Set up monitoring and alerts
4. ✅ Configure custom domain
5. ✅ Add to your CI/CD pipeline
6. ✅ Collect user feedback

---

**Happy Deploying! 🚀**

For questions or issues, create an issue on GitHub or check the main README.md.
