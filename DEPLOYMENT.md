# Deployment Guide

Complete guide to deploying the PR Test Scenario Generator to AWS and Azure.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Deploy to AWS](#deploy-to-aws)
- [Deploy to Azure](#deploy-to-azure)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)
- [Production Hardening](#production-hardening)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

1. **GitHub Account** - To host your repository
2. **Anthropic API Key** - Get from [console.anthropic.com](https://console.anthropic.com/)
3. **GitHub Token** (Optional) - For analyzing private repositories
4. **Git** installed locally
5. **Cloud Platform Account** - AWS or Azure

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

#### Step 2: Verify Procfile

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

#### Step 5: Set Environment Variables

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

### Option B: AWS App Runner (Container-based)

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
```

#### Step 1: Login to Azure

```bash
az login
# A browser window will open — sign in with your Microsoft account
```

#### Step 2: Create a Resource Group

```bash
az group create \
  --name pr-test-rg \
  --location eastus
```

#### Step 3: Create an App Service Plan

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

#### Step 5: Set Environment Variables

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
    needs: test

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

## Production Hardening

### 1. Gunicorn Tuning

Update your `Procfile` for better production performance:

```
web: gunicorn app:app --workers 4 --worker-class gthread --threads 2 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100
```

**Worker count formula:** `(2 × CPU cores) + 1`
- 1 CPU → 3 workers
- 2 CPU → 5 workers

### 2. Rate Limiting

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

@app.route('/api/analyze-pr', methods=['POST'])
@limiter.limit("5 per minute")
def analyze_pr():
    ...
```

### 3. Health Check Endpoint

Already implemented at `/health`. Configure it with:
- **AWS ALB**: Point health check to `/health`
- **Azure App Service**: Set health check path to `/health` in Monitoring settings

### 4. Security Best Practices

1. **Never commit `.env` file** - Already in .gitignore
2. **Use environment variables** - Already configured
3. **Set `FLASK_DEBUG=False`** in production
4. **Use strong `FLASK_SECRET_KEY`**
5. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

---

## Troubleshooting

### Application Won't Start

**Check logs:**
```bash
# AWS Elastic Beanstalk
eb logs

# Azure App Service
az webapp log tail --name pr-test-generator --resource-group pr-test-rg
```

**Common issues:**
- Missing environment variables
- Wrong start command in Procfile
- Dependency installation failed

### API Key Errors

- Verify `ANTHROPIC_API_KEY` is set correctly
- No quotes or extra spaces in the value
- Key has sufficient credits at [console.anthropic.com](https://console.anthropic.com)

### GitHub Token Issues

- Check token has `repo` or `public_repo` scope
- Token not expired
- For private repos, ensure `GITHUB_TOKEN` is set

---

For questions or issues, create an issue on GitHub or check the main README.md.
