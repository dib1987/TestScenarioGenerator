# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run web app (port 5000)
python app.py

# Run CLI version
python main.py

# Run tests
pytest tests/ -v

# Format code
black src/ app.py main.py

# Lint
pylint src/ app.py
```

### Deployment
```bash
# CI/CD auto-deploys to AWS EB on every push to main via GitHub Actions.
# Health check: curl http://test-scenario-generator-env.eba-akwiabyh.us-east-1.elasticbeanstalk.com/health
```

## Architecture

### Request Flow
```
User Input (GitHub PR URL or raw diff)
  → app.py routes (/api/analyze-pr or /api/analyze-diff)
  → src/git_analyzer.py  — fetches diff from GitHub API (or local git)
  → src/code_analyzer.py — parses diff into structured format, identifies change types
  → src/test_generator.py — calls AWS Bedrock (Claude Sonnet 4.5) to generate scenarios
  → Returns JSON: { scenarios (HTML), structured_test_cases (array), test_code, pr_info, analysis }
```

### Key Modules
- **[app.py](app.py)** — Flask app with two API endpoints: `/api/analyze-pr` (GitHub URL) and `/api/analyze-diff` (raw diff). Handles markdown→HTML conversion for the frontend.
- **[src/test_generator.py](src/test_generator.py)** — AWS Bedrock client. Three methods: `generate_test_scenarios()` (markdown), `generate_structured_test_cases()` (JSON array), `generate_automated_test_code()` (pytest code).
- **[src/code_analyzer.py](src/code_analyzer.py)** — Parses raw git diff text; `identify_change_types()` detects new/modified functions, API endpoints, DB changes, config changes via regex.
- **[src/git_analyzer.py](src/git_analyzer.py)** — `GitHubPRAnalyzer` fetches PR diffs and metadata via GitHub REST API; `GitAnalyzer` handles local repos via GitPython.

### AI Integration
- Model: `us.anthropic.claude-sonnet-4-5-20250929-v1:0` via AWS Bedrock (`bedrock-runtime`)
- Auth: IAM role on EC2 (production) or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env vars (local/CI)
- Three-stage generation: scenarios (markdown) → structured JSON test cases → optional pytest code
- Timeouts: nginx 300s, ALB 300s, gunicorn 120s — Bedrock calls can be slow

### Port Differences
- Local `python app.py`: port **5000**
- Production (AWS EB / gunicorn / Docker): port **8000**

### Environment Variables
Copy `.env.example` to `.env`. Required:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (default `us-east-1`)

Optional:
- `GITHUB_TOKEN` — needed for private repos or to avoid GitHub rate limits
- `APP_USERNAME` / `APP_PASSWORD` — enables basic auth on the web UI
- `FLASK_SECRET_KEY` — set only in EB Console in production, never in config files
- `DEFAULT_MODEL`, `MAX_TOKENS`, `TEMPERATURE`

### Frontend
Single-page app in [templates/index.html](templates/index.html) with vanilla JS in [static/js/app.js](static/js/app.js). Two tabs: GitHub PR URL input and manual diff input. Results display: PR info card, change summary, rendered test scenarios, filterable test case grid, generated test code.
