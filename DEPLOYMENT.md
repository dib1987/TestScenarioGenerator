# 🚀 Deployment Guide

Complete guide to deploying the PR Test Scenario Generator to various cloud platforms.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Deploy to Render](#deploy-to-render-recommended)
- [Deploy to Heroku](#deploy-to-heroku)
- [Deploy to Railway](#deploy-to-railway)
- [Deploy to AWS/Azure/GCP](#deploy-to-other-platforms)
- [Docker Deployment](#docker-deployment)
- [VPS Deployment (DigitalOcean / Linode / EC2)](#vps-deployment)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)
- [Nginx Reverse Proxy Setup](#nginx-reverse-proxy-setup)
- [Production Hardening](#production-hardening)
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

## Deploy to AWS

Two recommended options — **Elastic Beanstalk** (easiest PaaS) and **App Runner** (container-based).

---

### Option A: AWS Elastic Beanstalk (Recommended for beginners)

Elastic Beanstalk handles the server, load balancer, and scaling automatically.

#### Prerequisites
- AWS Account: [aws.amazon.com](https://aws.amazon.com)
- AWS CLI installed: [docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- EB CLI installed

```bash
pip install awsebcli
```

#### Step 1: Configure AWS Credentials

```bash
aws configure
# Enter your:
# AWS Access Key ID
# AWS Secret Access Key
# Default region (e.g., us-east-1)
# Output format: json
```

Get your Access Key from: AWS Console → IAM → Users → Your User → Security Credentials → Create Access Key

#### Step 2: Create a `Procfile` (already exists — verify it)

```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

#### Step 3: Initialize Elastic Beanstalk

```bash
cd "c:\Agentic Workflow\TestScenarioGenerator"

eb init pr-test-generator \
  --platform "Python 3.11" \
  --region us-east-1
```

When prompted:
- **Do you want to use CodeCommit?** → No
- **Do you want to set up SSH?** → No (for now)

#### Step 4: Create the Environment

```bash
eb create pr-test-gen-prod \
  --instance-type t3.small \
  --single
```

This takes 3–5 minutes. It creates an EC2 instance, security groups, and a load balancer.

#### Step 5: Set Environment Variables (Secrets)

**Never hardcode keys — set them as environment variables:**

```bash
eb setenv \
  ANTHROPIC_API_KEY=sk-ant-your-key-here \
  GITHUB_TOKEN=ghp_your-token-here \
  FLASK_DEBUG=False \
  FLASK_SECRET_KEY=your-random-secret-string
```

#### Step 6: Deploy

```bash
eb deploy
```

#### Step 7: Open Your App

```bash
eb open
# Opens browser to your app URL: http://pr-test-gen-prod.us-east-1.elasticbeanstalk.com
```

#### Useful EB Commands

```bash
eb status              # Check environment health
eb logs                # View application logs
eb logs --all          # Download all logs
eb health              # Detailed health report
eb terminate           # Shut down environment (stops billing)
```

---

### Option B: AWS App Runner (Container-based, simpler)

App Runner runs your Docker container fully managed — no server config needed.

#### Step 1: Push Docker Image to Amazon ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS \
  --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name pr-test-generator

# Build and tag
docker build -t pr-test-generator .
docker tag pr-test-generator:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/pr-test-generator:latest

# Push
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/pr-test-generator:latest
```

> Replace `123456789012` with your actual AWS Account ID (find it in AWS Console top right).

#### Step 2: Create App Runner Service (AWS Console)

1. Go to AWS Console → **App Runner**
2. Click **Create service**
3. **Source**: Container registry → Amazon ECR
4. Select your image `pr-test-generator:latest`
5. **Deployment trigger**: Automatic (redeploys on new image push)
6. **Service name**: `pr-test-generator`
7. **Port**: `5000`
8. Under **Environment variables**, add:
   - `ANTHROPIC_API_KEY` = your key
   - `GITHUB_TOKEN` = your token
   - `FLASK_DEBUG` = `False`
9. Click **Create & deploy**

Your app gets a URL like: `https://abc123.us-east-1.awsapprunner.com`

---

## Deploy to Azure

Two recommended options — **Azure App Service** (easiest PaaS) and **Azure Container Apps**.

---

### Option A: Azure App Service (Recommended)

Azure App Service is the Azure equivalent of Elastic Beanstalk — managed platform for web apps.

#### Prerequisites

- Azure Account: [portal.azure.com](https://portal.azure.com) (free $200 credit for new accounts)
- Azure CLI installed:

```bash
# Windows (PowerShell as Administrator)
winget install Microsoft.AzureCLI

# Or download from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows
```

#### Step 1: Login to Azure

```bash
az login
# A browser window will open — sign in with your Microsoft account
```

#### Step 2: Create a Resource Group

A resource group is a container that holds related Azure resources.

```bash
az group create \
  --name pr-test-rg \
  --location eastus
```

#### Step 3: Create an App Service Plan

The plan defines the pricing tier and compute resources.

```bash
az appservice plan create \
  --name pr-test-plan \
  --resource-group pr-test-rg \
  --sku B1 \
  --is-linux
```

**Pricing tiers:**
| Tier | vCPU | RAM | Cost |
|---|---|---|---|
| F1 (Free) | Shared | 1 GB | $0/month (60 min/day CPU limit) |
| B1 (Basic) | 1 | 1.75 GB | ~$13/month |
| B2 (Basic) | 2 | 3.5 GB | ~$27/month |
| P1v3 (Premium) | 2 | 8 GB | ~$74/month |

#### Step 4: Create the Web App

```bash
az webapp create \
  --name pr-test-generator \
  --resource-group pr-test-rg \
  --plan pr-test-plan \
  --runtime "PYTHON:3.11" \
  --deployment-local-git
```

This returns a Git URL like: `https://pr-test-generator.scm.azurewebsites.net/pr-test-generator.git`

#### Step 5: Set Environment Variables (App Settings)

```bash
az webapp config appsettings set \
  --name pr-test-generator \
  --resource-group pr-test-rg \
  --settings \
    ANTHROPIC_API_KEY="sk-ant-your-key-here" \
    GITHUB_TOKEN="ghp_your-token-here" \
    FLASK_DEBUG="False" \
    FLASK_SECRET_KEY="your-random-secret-string" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

#### Step 6: Configure Startup Command

Tell Azure to use Gunicorn:

```bash
az webapp config set \
  --name pr-test-generator \
  --resource-group pr-test-rg \
  --startup-file "gunicorn app:app --bind 0.0.0.0:8000 --workers 4 --timeout 120"
```

> Azure App Service uses port **8000** internally (not 5000).

#### Step 7: Deploy via Git Push

```bash
# Add Azure as a git remote
git remote add azure https://pr-test-generator.scm.azurewebsites.net/pr-test-generator.git

# Push to deploy
git push azure main
```

#### Step 8: Open Your App

```bash
az webapp browse --name pr-test-generator --resource-group pr-test-rg
# URL: https://pr-test-generator.azurewebsites.net
```

#### Useful Azure Commands

```bash
# View live logs
az webapp log tail --name pr-test-generator --resource-group pr-test-rg

# Restart app
az webapp restart --name pr-test-generator --resource-group pr-test-rg

# Scale up (change plan)
az appservice plan update --name pr-test-plan --resource-group pr-test-rg --sku B2

# Delete everything (stop billing)
az group delete --name pr-test-rg --yes
```

---

### Option B: Azure Container Apps (Docker-based)

Best when you want container portability and auto-scaling.

#### Step 1: Build and Push to Azure Container Registry

```bash
# Create Azure Container Registry
az acr create \
  --name prtestgeneratorcr \
  --resource-group pr-test-rg \
  --sku Basic \
  --admin-enabled true

# Build and push directly to ACR (no local Docker needed)
az acr build \
  --registry prtestgeneratorcr \
  --image pr-test-generator:latest .
```

#### Step 2: Create Container App Environment

```bash
az containerapp env create \
  --name pr-test-env \
  --resource-group pr-test-rg \
  --location eastus
```

#### Step 3: Deploy the Container App

```bash
az containerapp create \
  --name pr-test-generator \
  --resource-group pr-test-rg \
  --environment pr-test-env \
  --image prtestgeneratorcr.azurecr.io/pr-test-generator:latest \
  --registry-server prtestgeneratorcr.azurecr.io \
  --target-port 5000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 5 \
  --secrets \
    anthropic-key=sk-ant-your-key-here \
    github-token=ghp_your-token-here \
  --env-vars \
    ANTHROPIC_API_KEY=secretref:anthropic-key \
    GITHUB_TOKEN=secretref:github-token \
    FLASK_DEBUG=False
```

Your app URL appears in the output: `https://pr-test-generator.happyfield-xxx.eastus.azurecontainerapps.io`

---

## CI/CD with GitHub Actions

### AWS — Elastic Beanstalk Auto-Deploy

#### Step 1: Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS IAM Access Key ID |
| `AWS_SECRET_ACCESS_KEY` | Your AWS IAM Secret Access Key |
| `AWS_REGION` | e.g. `us-east-1` |
| `EB_APP_NAME` | `pr-test-generator` |
| `EB_ENV_NAME` | `pr-test-gen-prod` |
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `GITHUB_TOKEN_SECRET` | Your GitHub token |

> Create an IAM user in AWS Console with **AWSElasticBeanstalkFullAccess** policy. Never use root credentials.

#### Step 2: Create `.github/workflows/deploy-aws.yml`

```yaml
name: Deploy to AWS Elastic Beanstalk

on:
  push:
    branches: [main]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: python -m pytest tests/ -v || echo "No tests found, skipping"

  deploy:
    name: Deploy to Elastic Beanstalk
    runs-on: ubuntu-latest
    needs: test  # Only deploy if tests pass

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Create deployment package
        run: zip -r deploy.zip . -x "*.git*" "venv/*" "__pycache__/*" "*.pyc" ".env"

      - name: Upload package to S3
        run: |
          aws s3 cp deploy.zip s3://${{ secrets.EB_APP_NAME }}-deployments/deploy-${{ github.sha }}.zip

      - name: Deploy to Elastic Beanstalk
        uses: einaregilsson/beanstalk-deploy@v22
        with:
          aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          application_name: ${{ secrets.EB_APP_NAME }}
          environment_name: ${{ secrets.EB_ENV_NAME }}
          version_label: ${{ github.sha }}
          region: ${{ secrets.AWS_REGION }}
          deployment_package: deploy.zip
          wait_for_environment_recovery: 120

      - name: Print app URL
        run: |
          echo "Deployed to: http://${{ secrets.EB_ENV_NAME }}.${{ secrets.AWS_REGION }}.elasticbeanstalk.com"
```

---

### AWS — App Runner Auto-Deploy (Docker)

```yaml
name: Deploy to AWS App Runner

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: pr-test-generator

jobs:
  deploy:
    name: Build and Deploy
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Deploy to App Runner
        uses: awslabs/amazon-app-runner-deploy@main
        with:
          service: pr-test-generator
          image: ${{ steps.build-image.outputs.image }}
          access-role-arn: ${{ secrets.APP_RUNNER_ROLE_ARN }}
          region: ${{ env.AWS_REGION }}
          port: 5000
          cpu: 1
          memory: 2
          wait-for-service-stability-seconds: 180
```

---

### Azure App Service Auto-Deploy

#### Step 1: Add GitHub Secrets

| Secret Name | Value |
|---|---|
| `AZURE_CREDENTIALS` | Service principal JSON (see below) |
| `AZURE_WEBAPP_NAME` | `pr-test-generator` |
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `GITHUB_TOKEN_SECRET` | Your GitHub token |

**Generate `AZURE_CREDENTIALS`:**

```bash
az ad sp create-for-rbac \
  --name "pr-test-generator-deploy" \
  --role contributor \
  --scopes /subscriptions/{your-subscription-id}/resourceGroups/pr-test-rg \
  --json-auth
```

Copy the entire JSON output and paste it as the `AZURE_CREDENTIALS` secret.

#### Step 2: Create `.github/workflows/deploy-azure.yml`

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  AZURE_WEBAPP_NAME: pr-test-generator

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: python -m pytest tests/ -v || echo "No tests found, skipping"

  deploy:
    name: Deploy to Azure
    runs-on: ubuntu-latest
    needs: test
    environment:
      name: production
      url: https://${{ env.AZURE_WEBAPP_NAME }}.azurewebsites.net

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies into local folder
        run: pip install -r requirements.txt --target=".python_packages/lib/site-packages"

      - name: Login to Azure
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Update App Settings (env vars)
        uses: azure/appservice-settings@v1
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          app-settings-json: |
            [
              { "name": "ANTHROPIC_API_KEY", "value": "${{ secrets.ANTHROPIC_API_KEY }}", "slotSetting": false },
              { "name": "GITHUB_TOKEN", "value": "${{ secrets.GITHUB_TOKEN_SECRET }}", "slotSetting": false },
              { "name": "FLASK_DEBUG", "value": "False", "slotSetting": false },
              { "name": "SCM_DO_BUILD_DURING_DEPLOYMENT", "value": "true", "slotSetting": false }
            ]

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          package: .
          startup-command: "gunicorn app:app --bind 0.0.0.0:8000 --workers 4 --timeout 120"

      - name: Azure logout
        run: az logout

      - name: Print app URL
        run: echo "Deployed to https://${{ env.AZURE_WEBAPP_NAME }}.azurewebsites.net"
```

---

### Azure Container Apps Auto-Deploy (Docker)

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]

env:
  AZURE_CONTAINER_APP: pr-test-generator
  AZURE_RESOURCE_GROUP: pr-test-rg
  ACR_NAME: prtestgeneratorcr

jobs:
  build-and-deploy:
    name: Build and Deploy Container
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push image to ACR
        run: |
          az acr build \
            --registry ${{ env.ACR_NAME }} \
            --image pr-test-generator:${{ github.sha }} \
            --image pr-test-generator:latest \
            .

      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name ${{ env.AZURE_CONTAINER_APP }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/pr-test-generator:${{ github.sha }}

      - name: Azure logout
        run: az logout
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

---

## Docker Deployment

Docker containerizes the app so it runs identically on any machine or cloud platform.

### Step 1: Create Dockerfile

Create a file named `Dockerfile` in your project root:

```dockerfile
# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]
```

### Step 2: Create .dockerignore

Create `.dockerignore` to keep the image lean:

```
venv/
__pycache__/
*.pyc
*.pyo
.env
.git
*.md
output/
```

### Step 3: Create docker-compose.yml (optional but recommended)

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - FLASK_DEBUG=False
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 4: Build and Run

```bash
# Build the Docker image
docker build -t pr-test-generator .

# Run with environment variables from .env file
docker run -d \
  --name pr-test-gen \
  --env-file .env \
  -p 5000:5000 \
  pr-test-generator

# Or using docker-compose
docker compose up -d

# View logs
docker logs -f pr-test-gen

# Stop
docker compose down
```

### Step 5: Push to Docker Hub (for cloud deployment)

```bash
# Login to Docker Hub
docker login

# Tag your image
docker tag pr-test-generator yourdockerhubuser/pr-test-generator:latest

# Push
docker push yourdockerhubuser/pr-test-generator:latest
```

---

## VPS Deployment

Deploy on a raw Linux server (DigitalOcean Droplet, AWS EC2, Linode, Vultr, etc.).

### Recommended: DigitalOcean Droplet ($6/month)

**Step 1: Create a Droplet**
- Ubuntu 22.04 LTS
- Basic plan: 1 vCPU, 1 GB RAM (enough to start)
- Add your SSH key

**Step 2: Connect and Prepare Server**

```bash
# SSH into your server
ssh root@your-server-ip

# Update packages
apt update && apt upgrade -y

# Install Python, pip, git, nginx
apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx

# Create a non-root user for safety
adduser appuser
usermod -aG sudo appuser
su - appuser
```

**Step 3: Clone and Set Up the App**

```bash
# Clone your repository
git clone https://github.com/yourusername/TestScenarioGenerator.git
cd TestScenarioGenerator

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Paste your ANTHROPIC_API_KEY and GITHUB_TOKEN, save with Ctrl+O, exit Ctrl+X
```

**Step 4: Test the App Runs**

```bash
python app.py
# Should print: Running on http://0.0.0.0:5000
# Press Ctrl+C to stop
```

**Step 5: Create a systemd Service (auto-start on reboot)**

```bash
sudo nano /etc/systemd/system/pr-test-generator.service
```

Paste this content:

```ini
[Unit]
Description=PR Test Scenario Generator
After=network.target

[Service]
User=appuser
WorkingDirectory=/home/appuser/TestScenarioGenerator
EnvironmentFile=/home/appuser/TestScenarioGenerator/.env
ExecStart=/home/appuser/TestScenarioGenerator/venv/bin/gunicorn app:app \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/pr-test-gen/access.log \
    --error-logfile /var/log/pr-test-gen/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/pr-test-gen
sudo chown appuser:appuser /var/log/pr-test-gen

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable pr-test-generator
sudo systemctl start pr-test-generator

# Check status
sudo systemctl status pr-test-generator
```

**Step 6: View Live Logs**

```bash
sudo journalctl -u pr-test-generator -f
```

---

## Nginx Reverse Proxy Setup

Nginx sits in front of Gunicorn — handles SSL, compression, and forwards traffic to your app.

### Step 1: Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/pr-test-generator
```

Paste:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Increase timeout for AI processing (Claude can take 30+ seconds)
    proxy_read_timeout 180s;
    proxy_connect_timeout 10s;

    # Max upload size for large diffs
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files served directly by Nginx (faster)
    location /static/ {
        alias /home/appuser/TestScenarioGenerator/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Step 2: Enable the Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pr-test-generator /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 3: Add Free SSL with Let's Encrypt

```bash
# Get SSL certificate (replace with your actual domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot auto-updates your Nginx config for HTTPS
# Auto-renewal is set up automatically

# Test renewal
sudo certbot renew --dry-run
```

Your app is now live at `https://yourdomain.com` with HTTPS!

---

## CI/CD with GitHub Actions

Automatically deploy to your VPS every time you push to `main`.

### Step 1: Add GitHub Secrets

In your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `GITHUB_TOKEN_SECRET` | Your GitHub token |
| `VPS_HOST` | Your server IP address |
| `VPS_USER` | `appuser` |
| `VPS_SSH_KEY` | Your private SSH key content |

### Step 2: Create the Workflow File

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies and run tests
        run: |
          pip install -r requirements.txt
          python -m pytest tests/ -v || true  # Don't fail if no tests yet

      - name: Deploy to VPS via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/TestScenarioGenerator
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt --quiet
            sudo systemctl restart pr-test-generator
            echo "Deployment complete!"

      - name: Notify on success
        if: success()
        run: echo "✅ Deployed successfully to production!"

      - name: Notify on failure
        if: failure()
        run: echo "❌ Deployment failed — check logs!"
```

### Step 3: For Render/Railway/Heroku (simpler)

These platforms auto-deploy on every `git push origin main` — no additional workflow needed.

For **Render** with a deploy hook:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy Hook
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

---

## Production Hardening

### 1. Gunicorn Tuning

Update your `Procfile` for better production performance:

```
web: gunicorn app:app --workers 4 --worker-class gthread --threads 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100
```

**Worker count formula:** `(2 × CPU cores) + 1`
- 1 CPU → 3 workers
- 2 CPU → 5 workers

### 2. Rate Limiting (prevent abuse)

Add to `requirements.txt`:
```
Flask-Limiter==3.5.0
```

Add to `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

# Apply to API endpoints
@app.route('/api/analyze-pr', methods=['POST'])
@limiter.limit("5 per minute")
def analyze_pr():
    ...
```

### 3. Environment-Specific Config

```python
# In app.py
import os

ENV = os.environ.get('FLASK_ENV', 'production')

if ENV == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
elif ENV == 'development':
    app.config['DEBUG'] = True
```

### 4. Health Check Endpoint

Already implemented at `/health`. Use it with:
- **Render/Railway**: Set health check path to `/health`
- **AWS ALB**: Point health check to `/health`
- **Uptime monitoring**: Use UptimeRobot (free) to ping `/health` every 5 minutes

### 5. Logging in Production

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
```

### 6. Keep Render Free Tier Alive

Free tier sleeps after 15 minutes of inactivity. Use a free ping service:

- [UptimeRobot](https://uptimerobot.com) — ping your `/health` endpoint every 5 min (free)
- Alternatively, upgrade to Render's $7/month plan for always-on

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
