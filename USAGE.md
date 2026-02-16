# 📖 Usage Guide - PR Test Scenario Generator

Complete guide on how to use the PR Test Scenario Generator to create comprehensive test scenarios from your code changes.

---

## Table of Contents
- [Web Interface Usage](#web-interface-usage)
- [CLI Usage](#cli-usage)
- [Example Workflows](#example-workflows)
- [Understanding the Output](#understanding-the-output)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🌐 Web Interface Usage

### Starting the Application

**On Windows:**
```bash
start_server.bat
```

**On macOS/Linux:**
```bash
python app.py
```

**Access the app:**
```
http://localhost:5000
```

---

### Main Interface Overview

When you open the application, you'll see:

**Header Section:**
- 🧪 **Title**: "PR Test Scenario Generator"
- 📝 **Subtitle**: Description of the tool

**Input Section:**
- Two tabs: "GitHub PR URL" and "Manual Diff"
- Input field for PR URL or diff text
- Checkbox for generating test code
- "Generate Test Scenarios" button

---

### Method 1: Analyze GitHub Pull Request

**Best for:** Analyzing existing PRs from GitHub repositories

#### Steps:

1. **Get PR URL**
   - Navigate to any GitHub pull request
   - Copy the URL from your browser
   - Example: `https://github.com/owner/repo/pull/123`

2. **Enter PR URL**
   - Make sure "GitHub PR URL" tab is selected (default)
   - Paste the URL into the input field
   - Example URLs you can try:
     ```
     https://github.com/anthropics/anthropic-sdk-python/pull/123
     https://github.com/pallets/flask/pull/5000
     https://github.com/psf/requests/pull/6000
     ```

3. **Optional: Enable Test Code Generation**
   - Check the box "Generate test code (Python/pytest)"
   - This will create actual runnable test code
   - Takes a bit longer but very useful

4. **Click "Generate Test Scenarios"**
   - The app will show a loading animation
   - Progress steps will be displayed:
     - ✓ Fetching PR data
     - ✓ Analyzing code changes
     - ✓ Generating test scenarios

5. **View Results**
   - **PR Information**: Title, author, branches
   - **Changes Summary**: Files changed, lines added/deleted
   - **File-by-File Analysis**: What changed in each file
   - **Test Scenarios**: Comprehensive test cases
   - **Test Code** (if requested): Ready-to-use Python code

6. **Download or Copy**
   - Click "Download MD" to save as Markdown
   - Click "Copy" to copy to clipboard
   - Click "Download" (test code) to save test file

---

### Method 2: Analyze Manual Git Diff

**Best for:** Local changes, custom diffs, non-GitHub repositories

#### Steps:

1. **Generate Git Diff**

   In your local repository:
   ```bash
   # Compare two branches
   git diff main..feature-branch > diff.txt

   # Or compare commits
   git diff abc123..def456 > diff.txt

   # Or view uncommitted changes
   git diff > diff.txt
   ```

2. **Copy Diff Content**
   - Open the diff file or copy from terminal
   - Select all content (Ctrl+A)
   - Copy (Ctrl+C)

3. **Switch to "Manual Diff" Tab**
   - Click the "Manual Diff" tab
   - You'll see a large text area

4. **Paste Diff**
   - Click in the text area
   - Paste your diff (Ctrl+V)
   - The diff should start with lines like:
     ```diff
     diff --git a/file.py b/file.py
     index abc123..def456 100644
     --- a/file.py
     +++ b/file.py
     ```

5. **Optional: Enable Test Code**
   - Check "Generate test code" if needed

6. **Generate**
   - Click "Generate Test Scenarios"
   - Wait for analysis (usually 10-30 seconds)

7. **View and Download Results**
   - Same as Method 1

---

## 💻 CLI Usage

### Starting CLI

```bash
cd "c:\Agentic Workflow\TestScenarioGenerator"
python main.py
```

---

### CLI Main Menu

You'll see:
```
======================================================================
PR Test Scenario Generator
======================================================================

How would you like to provide the code changes?
1. Local git repository (compare branches)
2. GitHub pull request URL
3. Enter git diff manually

Enter your choice (1-3):
```

---

### Option 1: Local Git Repository

**Best for:** Comparing branches in your local repo

1. **Select Option 1**
   ```
   Enter your choice (1-3): 1
   ```

2. **Enter Repository Path**
   ```
   Enter repository path (press Enter for current directory):
   ```
   - Press Enter for current directory
   - Or enter path like: `C:\Projects\MyRepo`

3. **Enter Base Branch**
   ```
   Enter base branch (e.g., 'main'):
   ```
   - Usually: `main` or `master`

4. **Enter Compare Branch**
   ```
   Enter compare branch (e.g., 'feature/new-feature'):
   ```
   - Your feature branch name

5. **Wait for Analysis**
   - Tool fetches diff
   - Analyzes changes
   - Generates scenarios
   - Shows results in terminal

6. **Optional: Generate Test Code**
   ```
   Would you like to generate actual test code? (y/n): y
   Enter programming language (default: python): python
   Enter testing framework (default: pytest): pytest
   ```

7. **Save Results**
   ```
   Would you like to save the results to a file? (y/n): y
   Enter filename (default: test_scenarios.md): my_test_scenarios.md
   ```

---

### Option 2: GitHub Pull Request URL

**Best for:** Analyzing PRs from GitHub

1. **Select Option 2**
   ```
   Enter your choice (1-3): 2
   ```

2. **Enter PR URL**
   ```
   Enter GitHub PR URL: https://github.com/owner/repo/pull/123
   ```

3. **Automatic Processing**
   - Fetches PR from GitHub
   - Shows PR title and author
   - Analyzes changes
   - Generates scenarios

4. **Follow prompts** for test code generation and saving

---

### Option 3: Manual Diff Entry

**Best for:** Custom diffs, quick tests

1. **Select Option 3**
   ```
   Enter your choice (1-3): 3
   ```

2. **Paste Diff**
   ```
   Paste your git diff (press Ctrl+D or Ctrl+Z when done):
   ```
   - Paste your diff content
   - Press Ctrl+Z then Enter (Windows)
   - Or Ctrl+D (Linux/Mac)

3. **Processing continues** automatically

---

## 📋 Example Workflows

### Workflow 1: Pre-PR Review

**Scenario:** Before creating a PR, generate test scenarios

```bash
# 1. Create your feature branch
git checkout -b feature/user-authentication

# 2. Make your changes
# ... code changes ...

# 3. Generate diff
git diff main > my_changes.diff

# 4. Use the tool (Web or CLI)
# Method A: Web Interface
start_server.bat
# Then paste diff in "Manual Diff" tab

# Method B: CLI
python main.py
# Select option 3, paste diff

# 5. Review test scenarios
# 6. Implement suggested tests
# 7. Create PR with comprehensive tests
```

---

### Workflow 2: PR Code Review

**Scenario:** Reviewing a teammate's PR

```bash
# 1. Get PR URL from GitHub
# Example: https://github.com/company/project/pull/456

# 2. Open web app
start_server.bat
# Navigate to http://localhost:5000

# 3. Paste PR URL
# 4. Click "Generate Test Scenarios"

# 5. Review generated scenarios
# 6. Add comments to PR with test suggestions
# 7. Share scenarios with PR author
```

---

### Workflow 3: Testing Sprint Planning

**Scenario:** Planning test coverage for multiple features

```bash
# 1. For each feature branch
for branch in feature-auth feature-api feature-ui
do
    # Generate diff
    git diff main..$branch > ${branch}_diff.txt

    # Analyze with tool
    # (Save results with branch name)
done

# 2. Compile all test scenarios
# 3. Plan sprint testing tasks
# 4. Assign to QA team
```

---

## 📊 Understanding the Output

### Test Scenario Structure

Each generated test scenario includes:

#### 1. **Changes Summary**
```markdown
## Changes Summary
- Files changed: 5
- Lines added: 142
- Lines deleted: 38
- Main changes: Added user authentication, Updated API endpoints
```

#### 2. **Test Scenarios by Priority**

**High Priority Tests:**
```markdown
### Test Scenario 1: User Login Validation
**Type**: Unit Test
**Priority**: High
**Objective**: Verify user login with valid credentials

**Preconditions**:
- User exists in database
- Password is correctly hashed

**Test Steps**:
1. Call login() with valid username and password
2. Verify authentication token is returned
3. Verify token is valid for 24 hours
4. Verify user session is created

**Expected Results**:
- Status code: 200
- Response contains: auth_token, user_id, expires_at
- Token can be used for authenticated requests

**Edge Cases to Consider**:
- Empty username/password
- SQL injection attempts
- Concurrent login attempts
```

**Medium Priority Tests:**
```markdown
### Test Scenario 2: Password Reset Flow
**Type**: Integration Test
**Priority**: Medium
...
```

**Low Priority Tests:**
```markdown
### Test Scenario 3: UI Responsiveness
**Type**: UI Test
**Priority**: Low
...
```

#### 3. **Regression Tests**
```markdown
## Regression Tests

### R1: Existing API Endpoints
Verify that authentication changes don't break existing endpoints
- Test all public endpoints still accessible
- Test all protected endpoints require new token format
```

#### 4. **Performance Considerations**
```markdown
## Performance Tests

### P1: Login Response Time
- Target: < 200ms for successful login
- Load test: 100 concurrent users
```

#### 5. **Security Considerations**
```markdown
## Security Tests

### S1: Password Hashing
- Verify bcrypt with cost factor 12
- Ensure no plain text storage

### S2: Token Security
- JWT signed with secure secret
- No sensitive data in token payload
```

---

### Generated Test Code Structure

When you enable test code generation:

```python
"""
Generated Test Suite for PR #123
Auto-generated by PR Test Scenario Generator
"""

import pytest
from app.auth import login, logout
from app.models import User

class TestUserAuthentication:
    """Test cases for user authentication feature"""

    def test_valid_login(self):
        """Test user login with valid credentials"""
        # Setup
        user = User.create(username="test", password="secure123")

        # Execute
        result = login("test", "secure123")

        # Assert
        assert result.success is True
        assert result.token is not None
        assert result.token.expires_in == 86400  # 24 hours

    def test_invalid_password(self):
        """Test login fails with wrong password"""
        # Setup
        user = User.create(username="test", password="secure123")

        # Execute
        result = login("test", "wrongpassword")

        # Assert
        assert result.success is False
        assert result.error == "Invalid credentials"

    # ... more tests
```

---

## ✅ Best Practices

### 1. **Analyzing PRs**

**Do:**
- ✅ Analyze PRs before final review
- ✅ Use scenarios as checklist for testing
- ✅ Share scenarios with PR author
- ✅ Save scenarios for documentation

**Don't:**
- ❌ Skip manual review (AI assists, doesn't replace)
- ❌ Trust all scenarios blindly
- ❌ Ignore context of your application

---

### 2. **Using Test Scenarios**

**Do:**
- ✅ Prioritize high-priority tests first
- ✅ Customize scenarios to your context
- ✅ Add domain-specific edge cases
- ✅ Use as starting point for test implementation

**Don't:**
- ❌ Copy test code without understanding
- ❌ Skip edge cases
- ❌ Ignore security tests

---

### 3. **API Key Management**

**Do:**
- ✅ Use separate API keys for dev/prod
- ✅ Monitor API usage
- ✅ Set up billing alerts
- ✅ Rotate keys periodically

**Don't:**
- ❌ Share API keys in code
- ❌ Commit `.env` file
- ❌ Use same key across teams

---

### 4. **Team Usage**

**Do:**
- ✅ Deploy to cloud for team access
- ✅ Document internal best practices
- ✅ Create templates for common scenarios
- ✅ Share successful test cases

**Don't:**
- ❌ Generate scenarios for trivial changes
- ❌ Overload API with large diffs
- ❌ Skip human review

---

## 🔧 Troubleshooting

### Issue: "Invalid PR URL"

**Symptoms:**
```
Error: Invalid GitHub PR URL format
```

**Solutions:**
1. Verify URL format:
   ```
   ✅ https://github.com/owner/repo/pull/123
   ❌ github.com/owner/repo/pull/123 (missing https://)
   ❌ https://github.com/owner/repo (missing /pull/123)
   ```

2. Ensure it's a pull request URL, not:
   - Issue URL: `.../issues/123`
   - Commit URL: `.../commit/abc123`
   - Repository URL: `.../owner/repo`

---

### Issue: "GitHub API Rate Limit"

**Symptoms:**
```
Error: API rate limit exceeded
```

**Solutions:**
1. Add `GITHUB_TOKEN` to `.env`:
   ```env
   GITHUB_TOKEN=ghp_your_token_here
   ```

2. Wait 1 hour (limit resets)

3. Upgrade to authenticated requests (5000/hour vs 60/hour)

---

### Issue: "API Key Error"

**Symptoms:**
```
Error: Invalid API request. Check your Anthropic API key
```

**Solutions:**
1. Verify `.env` file exists with:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Check API key at [console.anthropic.com](https://console.anthropic.com/)

3. Verify key has credits

4. Restart server after updating `.env`

---

### Issue: "Diff Too Large"

**Symptoms:**
- Very slow processing
- Timeouts
- Incomplete results

**Solutions:**
1. Split large PRs into smaller chunks

2. Analyze specific files:
   ```bash
   git diff main -- path/to/specific/file.py > small.diff
   ```

3. Focus on critical changes first

---

### Issue: "Poor Quality Scenarios"

**Symptoms:**
- Generic or irrelevant tests
- Missing edge cases
- Not matching your tech stack

**Solutions:**
1. **Provide more context** in diff:
   - Include relevant files
   - Don't just diff one file in isolation

2. **Use PR context** (web interface):
   - PR descriptions help Claude understand intent
   - Use GitHub PR URL instead of raw diff

3. **Customize the output**:
   - Edit `src/test_generator.py`
   - Adjust prompts to your domain
   - Add examples for your tech stack

---

### Issue: "Server Won't Start"

**Symptoms:**
```
Error: Port 5000 already in use
```

**Solutions:**
1. **Check what's using port 5000:**
   ```bash
   netstat -ano | findstr :5000
   ```

2. **Kill the process:**
   ```bash
   taskkill /PID <process_id> /F
   ```

3. **Or use different port:**
   Edit `.env`:
   ```env
   PORT=8000
   ```

---

## 📚 Additional Resources

### Documentation Files
- [README.md](README.md) - Project overview and installation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md) - Quick 15-min deployment
- [CLAUDE.md](CLAUDE.md) - Development and integration guide

### External Resources
- [Anthropic API Docs](https://docs.anthropic.com/)
- [GitHub API Docs](https://docs.github.com/en/rest)
- [pytest Documentation](https://docs.pytest.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 💡 Tips & Tricks

### Tip 1: Keyboard Shortcuts (Web Interface)
- `Ctrl+V`: Paste PR URL or diff
- `Ctrl+A`: Select all output
- `Ctrl+C`: Copy scenarios
- `Enter`: Submit form (when focused)

### Tip 2: Batch Processing (CLI)
```bash
# Process multiple PRs
for pr in 123 124 125; do
    python main.py --pr "https://github.com/owner/repo/pull/$pr"
done
```

### Tip 3: Custom Templates
Edit `src/test_generator.py` to add your templates:
```python
# Add custom test frameworks
frameworks = {
    'jest': 'JavaScript/Jest',
    'junit': 'Java/JUnit',
    'pytest': 'Python/pytest',
    # Add yours here
}
```

### Tip 4: Integration with CI/CD
Add to your pipeline:
```yaml
# .github/workflows/test-scenarios.yml
name: Generate Test Scenarios
on: [pull_request]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate scenarios
        run: |
          python main.py --pr ${{ github.event.pull_request.html_url }}
      - name: Comment on PR
        # Post scenarios as PR comment
```

---

## 🎯 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│         PR TEST SCENARIO GENERATOR - QUICK REF          │
├─────────────────────────────────────────────────────────┤
│ START SERVER:                                           │
│   Windows: start_server.bat                             │
│   Linux/Mac: python app.py                              │
│                                                          │
│ ACCESS:                                                  │
│   Local: http://localhost:5000                          │
│   Network: http://192.168.1.192:5000                    │
│                                                          │
│ INPUTS:                                                  │
│   • GitHub PR URL                                        │
│   • Manual git diff                                      │
│   • Local repo branches                                  │
│                                                          │
│ OUTPUTS:                                                 │
│   • Test scenarios (Markdown)                            │
│   • Test code (Python/pytest)                            │
│   • Coverage analysis                                    │
│                                                          │
│ STOP SERVER:                                             │
│   Press Ctrl+C in terminal                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🆘 Need Help?

1. **Check this guide first** - Most questions answered here
2. **Review [README.md](README.md)** - Installation and setup
3. **Check [DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment
4. **Open GitHub Issue** - Report bugs or request features
5. **Contact team lead** - Internal questions

---

**Happy Testing! 🚀**

Generated by PR Test Scenario Generator
