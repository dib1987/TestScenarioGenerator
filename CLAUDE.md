# Claude AI Integration Guide
## PR Test Scenarios Generation - Agentic Workflow

### Overview
This guide will help you build an agentic workflow that analyzes Pull Request differences and automatically generates comprehensive test scenarios using Claude AI.

---

## What You'll Build

An automated system that:
1. Reads PR diff files (git diff output)
2. Analyzes code changes to understand impact
3. Generates relevant test scenarios covering:
   - Unit tests
   - Integration tests
   - Edge cases
   - Regression scenarios
   - Performance considerations

---

## Prerequisites

### 1. Anthropic API Key
- Sign up at: https://console.anthropic.com/
- Navigate to API Keys section
- Create a new API key
- Store it securely (you'll need it for environment variables)

### 2. VS Code Setup
- Install VS Code
- Install the following extensions:
  - Python (if using Python)
  - GitHub Pull Requests and Issues
  - GitLens (helpful for git operations)

### 3. Programming Environment
Choose your preferred language:
- **Python** (recommended for beginners)
- **TypeScript/JavaScript** (Node.js)
- **Any language with HTTP client capabilities**

---

## Architecture Overview

```
┌─────────────────┐
│   PR Created    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extract Diff   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse Changes  │
│  - Files        │
│  - Functions    │
│  - Logic        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Claude Agent   │
│  - Analyze      │
│  - Generate     │
│  - Validate     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Output Tests    │
│  - Scenarios    │
│  - Test Cases   │
│  - Edge Cases   │
└─────────────────┘
```

---

## Step-by-Step Implementation

### Step 1: Environment Setup

Create a `.env` file in your project root:
```env
ANTHROPIC_API_KEY=your_api_key_here
```

### Step 2: Install Dependencies

**For Python:**
```bash
pip install anthropic python-dotenv gitpython
```

**For Node.js:**
```bash
npm install @anthropic-ai/sdk dotenv simple-git
```

### Step 3: Basic Claude Integration

**Python Example:**
```python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

def generate_test_scenarios(pr_diff: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze the following PR diff and generate comprehensive test scenarios:

{pr_diff}

Please provide:
1. Unit test scenarios
2. Integration test scenarios
3. Edge cases to consider
4. Potential regression risks
5. Performance testing suggestions

Format the output as structured test cases."""
            }
        ]
    )
    return message.content[0].text
```

**Node.js Example:**
```javascript
import Anthropic from '@anthropic-ai/sdk';
import dotenv from 'dotenv';

dotenv.config();

const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
});

async function generateTestScenarios(prDiff) {
    const message = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4000,
        messages: [{
            role: 'user',
            content: `Analyze the following PR diff and generate comprehensive test scenarios:

${prDiff}

Please provide:
1. Unit test scenarios
2. Integration test scenarios
3. Edge cases to consider
4. Potential regression risks
5. Performance testing suggestions

Format the output as structured test cases.`
        }]
    });
    
    return message.content[0].text;
}
```

### Step 4: Extract PR Diff

**Python with GitPython:**
```python
import git

def get_pr_diff(repo_path: str, base_branch: str = "main", head_branch: str = "HEAD") -> str:
    repo = git.Repo(repo_path)
    diff = repo.git.diff(f"{base_branch}...{head_branch}")
    return diff
```

**Node.js with simple-git:**
```javascript
import simpleGit from 'simple-git';

async function getPRDiff(repoPath, baseBranch = 'main', headBranch = 'HEAD') {
    const git = simpleGit(repoPath);
    const diff = await git.diff([`${baseBranch}...${headBranch}`]);
    return diff;
}
```

### Step 5: Enhanced Agentic Workflow

Create a multi-step agentic system:

```python
class TestScenarioAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def analyze_changes(self, diff: str) -> dict:
        """Step 1: Analyze what changed"""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Analyze this PR diff and extract:
1. Modified files and their purposes
2. Changed functions/methods
3. Business logic changes
4. Database/API changes
5. Configuration changes

Diff:
{diff}

Return as JSON."""
            }]
        )
        return response.content[0].text
    
    def generate_scenarios(self, analysis: str, diff: str) -> str:
        """Step 2: Generate test scenarios based on analysis"""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""Based on this code analysis:
{analysis}

And the original diff:
{diff}

Generate comprehensive test scenarios with:
- Test case ID
- Description
- Preconditions
- Test steps
- Expected results
- Priority (High/Medium/Low)
- Type (Unit/Integration/E2E)"""
            }]
        )
        return response.content[0].text
    
    def validate_scenarios(self, scenarios: str) -> str:
        """Step 3: Validate and enhance scenarios"""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Review these test scenarios and:
1. Identify any gaps in coverage
2. Suggest additional edge cases
3. Flag any redundant tests
4. Recommend improvements

Scenarios:
{scenarios}"""
            }]
        )
        return response.content[0].text
```

---

## Advanced Features

### 1. Context Management
Store conversation history for multi-turn interactions:

```python
class ConversationalAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []
    
    def add_message(self, role: str, content: str):
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def generate(self, user_message: str) -> str:
        self.add_message("user", user_message)
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.add_message("assistant", assistant_message)
        
        return assistant_message
```

### 2. Structured Output with Tool Use

```python
tools = [
    {
        "name": "create_test_scenario",
        "description": "Creates a structured test scenario",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_id": {"type": "string"},
                "description": {"type": "string"},
                "type": {"type": "string", "enum": ["unit", "integration", "e2e"]},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "steps": {"type": "array", "items": {"type": "string"}},
                "expected_result": {"type": "string"}
            },
            "required": ["test_id", "description", "type", "priority"]
        }
    }
]
```

### 3. Prompt Caching for Efficiency

```python
def generate_with_caching(self, diff: str) -> str:
    response = self.client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=[
            {
                "type": "text",
                "text": """You are an expert QA engineer specializing in test scenario generation.
Your task is to analyze code changes and create comprehensive test plans.""",
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[{
            "role": "user",
            "content": f"Analyze this diff:\n{diff}"
        }]
    )
    return response.content[0].text
```

---

## Best Practices

### 1. Prompt Engineering
- Be specific about the output format you want
- Provide examples of good test scenarios
- Break complex tasks into smaller steps
- Use system prompts to set context

### 2. Error Handling
```python
import time

def call_claude_with_retry(client, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise
```

### 3. Cost Optimization
- Use prompt caching for repeated context
- Start with Claude Haiku for simple tasks
- Use Claude Sonnet for balanced performance
- Reserve Claude Opus for complex analysis

### 4. Output Validation
- Parse Claude's responses
- Validate against expected schema
- Handle incomplete or malformed responses
- Log all interactions for debugging

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Generate Test Scenarios

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install anthropic gitpython
      
      - name: Generate test scenarios
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python generate_scenarios.py
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const scenarios = fs.readFileSync('test_scenarios.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: scenarios
            });
```

---

## Example Project Structure

```
pr-test-generator/
├── .env
├── .gitignore
├── Claude.md
├── README.md
├── requirements.txt (or package.json)
├── src/
│   ├── __init__.py
│   ├── agent.py          # Main agent logic
│   ├── diff_parser.py    # Parse git diffs
│   ├── prompt_templates.py
│   └── output_formatter.py
├── tests/
│   └── test_agent.py
├── examples/
│   └── sample_diff.txt
└── output/
    └── test_scenarios.md
```

---

## Useful Resources

- **Anthropic Documentation**: https://docs.anthropic.com/
- **Claude API Reference**: https://docs.anthropic.com/en/api/
- **Prompt Engineering Guide**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- **GitHub API**: https://docs.github.com/en/rest

---

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `.env` file is in the project root
   - Check that `python-dotenv` is loading the file
   - Verify the key is correct in the Anthropic console

2. **Rate Limits**
   - Implement exponential backoff
   - Use prompt caching
   - Consider batching requests

3. **Poor Quality Output**
   - Refine your prompts
   - Provide more context
   - Use examples in prompts
   - Try a more capable model (Sonnet or Opus)

4. **Large Diffs**
   - Split large diffs into chunks
   - Focus on specific file types
   - Summarize changes first, then detail

---

## Next Steps

1. Start with a simple proof of concept
2. Test with small PRs first
3. Iterate on prompt quality
4. Add validation and error handling
5. Integrate with your CI/CD pipeline
6. Collect feedback and improve

Good luck with your agentic workflow! 🚀