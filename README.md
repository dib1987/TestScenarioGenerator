# 🧪 PR Test Scenario Generator

An intelligent **web application** that automatically generates comprehensive test scenarios from pull request code changes using **Claude AI** (Anthropic).

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 What Does This Tool Do?

This tool helps you:
1. **🌐 Web Interface** - Beautiful, modern UI accessible from any browser
2. **🔗 GitHub Integration** - Analyze PRs directly from GitHub URLs
3. **📝 Manual Diff Support** - Paste git diff output for instant analysis
4. **🤖 AI-Powered Analysis** - Claude AI understands your code changes
5. **✅ Comprehensive Test Scenarios** - Unit, integration, edge cases, and more
6. **💻 Automated Test Code** - Generate ready-to-use Python/pytest code
7. **☁️ Cloud-Ready** - Deploy to Render, Heroku, Railway in minutes

Perfect for developers and QA engineers who want to ensure thorough testing of code changes!

## Features

- Support for multiple input sources:
  - Local git repositories (compare branches)
  - GitHub pull requests (via URL)
  - Manual git diff input
- Intelligent code analysis to detect:
  - New/modified/deleted functions and classes
  - API endpoint changes
  - Database migrations
  - Configuration changes
- AI-powered test scenario generation using Claude
- Optional automated test code generation
- Save results to markdown files

## Prerequisites

- Python 3.8 or higher
- Git installed on your system
- Anthropic API key (for Claude AI) - [Get one here](https://console.anthropic.com/)
- (Optional) GitHub personal access token for private repositories

## Installation

### Step 1: Clone or Download This Project

If you have git:
```bash
git clone <your-repo-url>
cd "YouTube Analysis"
```

### Step 2: Create a Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_actual_claude_api_key_here
   GITHUB_TOKEN=your_github_token_here  # Optional
   ```

**How to get your Anthropic API key:**
- Go to https://console.anthropic.com/
- Sign up or log in
- Navigate to API Keys section
- Create a new API key

**How to get a GitHub token (optional):**
- Go to https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scopes: `repo` (for private repos) or just `public_repo`
- Generate and copy the token

## 🚀 Usage

### Option 1: Web Application (Recommended)

**Windows:**
```bash
start_server.bat
```

**macOS/Linux:**
```bash
python app.py
```

Then open your browser to `http://localhost:5000`

#### Using the Web Interface:
1. **GitHub PR Analysis**: Paste a PR URL (e.g., `https://github.com/owner/repo/pull/123`)
2. **Manual Diff**: Switch to "Manual Diff" tab and paste git diff output
3. **Generate**: Click "Generate Test Scenarios"
4. **Download**: Save results as Markdown or copy to clipboard

### Option 2: CLI Tool

Run the command-line interface:
```bash
python main.py
```

The tool will guide you through an interactive menu.

### Usage Examples

#### Example 1: Analyze Local Repository

1. Run: `python main.py`
2. Choose option `1` (Local git repository)
3. Enter repository path (or press Enter for current directory)
4. Enter base branch: `main`
5. Enter compare branch: `feature/my-new-feature`

#### Example 2: Analyze GitHub PR

1. Run: `python main.py`
2. Choose option `2` (GitHub pull request URL)
3. Enter PR URL: `https://github.com/owner/repo/pull/123`

#### Example 3: Manual Diff

1. Run: `python main.py`
2. Choose option `3` (Enter git diff manually)
3. Paste your diff content
4. Press Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows) when done

### Sample Output

The tool will generate:

```markdown
# Generated Test Scenarios

## Changes Summary
- Files changed: 3
- Lines added: 45
- Lines deleted: 12

## Test Scenarios

### 1. Unit Test: Test New Authentication Function
**Type**: Unit Test
**Objective**: Verify that the new login function correctly validates credentials
**Priority**: High
**Steps**:
1. Call login() with valid credentials
2. Verify response contains auth token
3. Call login() with invalid credentials
4. Verify appropriate error is returned
...
```

## ☁️ Cloud Deployment

### Deploy to Render (Recommended - Free Tier Available)

1. **Fork/Push this repo to GitHub**

2. **Go to [render.com](https://render.com)** and sign up

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select this repository

4. **Configure**:
   - **Name**: `pr-test-generator` (or your choice)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. **Add Environment Variables**:
   - Click "Environment" tab
   - Add: `ANTHROPIC_API_KEY` = `your_api_key_here`
   - Add: `GITHUB_TOKEN` = `your_token_here` (optional)

6. **Deploy** - Render will automatically deploy!

Your app will be live at: `https://your-app-name.onrender.com`

### Deploy to Heroku

1. **Install Heroku CLI**:
   ```bash
   # Windows (Chocolatey)
   choco install heroku-cli

   # macOS
   brew install heroku/brew/heroku
   ```

2. **Login and deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set ANTHROPIC_API_KEY=your_key_here
   heroku config:set GITHUB_TOKEN=your_token_here
   git push heroku main
   heroku open
   ```

### Deploy to Railway

1. **Visit [railway.app](https://railway.app)**
2. **Click "Start a New Project"**
3. **"Deploy from GitHub repo"**
4. **Select your repository**
5. **Add environment variables** in Settings:
   - `ANTHROPIC_API_KEY`
   - `GITHUB_TOKEN` (optional)
6. **Deploy automatically!**

### Deploy to Any Cloud Platform

The app includes a `Procfile` for easy deployment. Just set these environment variables:
- `ANTHROPIC_API_KEY` (required)
- `GITHUB_TOKEN` (optional, for private repos)
- `PORT` (automatically set by most platforms)

## Project Structure

```
TestScenarioGenerator/
├── app.py                    # Flask web application (Main)
├── main.py                   # CLI version (Alternative)
├── requirements.txt          # Python dependencies
├── Procfile                  # Cloud deployment config
├── runtime.txt              # Python version for deployment
├── start_server.bat         # Windows startup script
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── README.md                # This file
├── CLAUDE.md                # Project documentation & guide
├── src/                     # Core application logic
│   ├── __init__.py           # Package initialization
│   ├── git_analyzer.py       # Git & GitHub API operations
│   ├── code_analyzer.py      # Code change analysis
│   └── test_generator.py     # Claude AI integration
├── templates/               # HTML templates
│   └── index.html            # Main web interface
├── static/                  # Static assets
│   ├── css/
│   │   └── style.css         # Application styles
│   └── js/
│       └── app.js            # Frontend JavaScript
├── config/                  # Configuration files
│   └── config.yaml.example
└── tests/                   # Unit tests (future)
```

## How It Works

1. **Git Analysis**: Extracts diff information from your specified source
2. **Code Parsing**: Analyzes the diff to understand:
   - What files changed
   - What functions/classes were added or modified
   - What type of changes were made
3. **AI Generation**: Sends the analyzed changes to Claude AI with a specialized prompt
4. **Test Scenarios**: Claude generates comprehensive test scenarios covering:
   - Unit tests
   - Integration tests
   - Edge cases
   - Security considerations
   - Performance implications
5. **Test Code**: Optionally generates actual runnable test code

## Customization

### Changing the AI Model

Edit the `DEFAULT_MODEL` in your `.env` file:
```
DEFAULT_MODEL=claude-opus-4-6  # For more powerful analysis
```

### Adjusting Output Length

Modify `MAX_TOKENS` in `.env`:
```
MAX_TOKENS=8192  # For longer, more detailed scenarios
```

### Custom Prompts

Edit the `_build_prompt()` method in [src/test_generator.py](src/test_generator.py) to customize how test scenarios are generated.

## Troubleshooting

### "Not a git repository" error
- Make sure you're running the tool in a directory that's a git repository
- Or provide the full path to a git repository when prompted

### "Invalid API key" error
- Check that your `.env` file has the correct `ANTHROPIC_API_KEY`
- Make sure there are no extra spaces or quotes around the key

### "Module not found" error
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

### GitHub API rate limiting
- Add a `GITHUB_TOKEN` to your `.env` file
- Authenticated requests have much higher rate limits

## Contributing

This is a learning project! Feel free to:
- Add support for more programming languages
- Improve diff parsing logic
- Add more test scenario types
- Create a web interface
- Add database support to save historical test scenarios

## Future Enhancements

- [ ] Support for GitLab and Bitbucket
- [ ] Web interface for easier use
- [ ] Database to track test scenarios over time
- [ ] Integration with CI/CD pipelines
- [ ] Support for multiple AI models
- [ ] Test coverage analysis
- [ ] Automatic test execution

## Learning Resources

- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Python Testing with pytest](https://docs.pytest.org/)

## License

MIT License - Feel free to use and modify as needed!

## Questions or Issues?

If you encounter any problems or have questions:
1. Check the troubleshooting section above
2. Review the code comments in the source files
3. Create an issue in the repository

---

Happy Testing! 🚀
