"""
Test Generator Module
Uses Claude AI to generate comprehensive test scenarios from code changes.
"""

from anthropic import Anthropic
from typing import Dict, List
import os


class TestScenarioGenerator:
    """Generates test scenarios using Claude AI."""

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the Test Scenario Generator.

        Args:
            api_key: Anthropic API key (if not provided, uses ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate_test_scenarios(
        self,
        diff_summary: str,
        parsed_diff: List[Dict],
        change_types: Dict[str, List[str]],
        pr_context: Dict = None
    ) -> str:
        """
        Generate comprehensive test scenarios based on code changes.

        Args:
            diff_summary: Human-readable summary of changes
            parsed_diff: Structured diff information
            change_types: Categorized change types
            pr_context: Optional PR information (title, description, etc.)

        Returns:
            Generated test scenarios as a string
        """
        # Build the prompt for Claude
        prompt = self._build_prompt(diff_summary, parsed_diff, change_types, pr_context)

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract the response
        test_scenarios = response.content[0].text
        return test_scenarios

    def _build_prompt(
        self,
        diff_summary: str,
        parsed_diff: List[Dict],
        change_types: Dict[str, List[str]],
        pr_context: Dict = None
    ) -> str:
        """
        Build a comprehensive prompt for Claude.

        Args:
            diff_summary: Summary of changes
            parsed_diff: Parsed diff data
            change_types: Categorized changes
            pr_context: PR context information

        Returns:
            Formatted prompt string
        """
        prompt = """You are an expert software testing engineer. Your task is to analyze code changes from a pull request and generate comprehensive test scenarios.

## Code Changes Summary
"""
        prompt += diff_summary + "\n\n"

        # Add PR context if available
        if pr_context:
            prompt += "## Pull Request Context\n"
            prompt += f"Title: {pr_context.get('title', 'N/A')}\n"
            prompt += f"Description: {pr_context.get('description', 'N/A')}\n\n"

        # Add change types
        prompt += "## Types of Changes Detected\n"
        for change_type, changes in change_types.items():
            if changes:
                prompt += f"\n### {change_type.replace('_', ' ').title()}\n"
                for change in changes:
                    prompt += f"- {change}\n"

        # Add detailed file changes
        prompt += "\n## Detailed File Changes\n"
        for file_change in parsed_diff[:5]:  # Limit to first 5 files for token efficiency
            prompt += f"\n### File: {file_change['file_path']}\n"
            prompt += f"Additions: {len(file_change['additions'])} lines\n"
            prompt += f"Deletions: {len(file_change['deletions'])} lines\n"

            if file_change['additions']:
                prompt += "\nKey additions:\n"
                for line in file_change['additions'][:10]:  # First 10 additions
                    if line.strip():
                        prompt += f"  + {line}\n"

        # Add instructions for test generation
        prompt += """

## Your Task
Generate comprehensive test scenarios for these code changes. Include:

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test how components work together
3. **Edge Cases**: Boundary conditions and error scenarios
4. **Regression Tests**: Ensure existing functionality still works
5. **Security Tests**: Check for potential security issues (if applicable)
6. **Performance Tests**: Check for performance implications (if applicable)

For each test scenario, provide:
- **Test Name**: Clear, descriptive name
- **Test Type**: Unit/Integration/E2E/etc.
- **Objective**: What this test verifies
- **Steps**: How to execute the test
- **Expected Result**: What should happen
- **Priority**: High/Medium/Low

Format your response as a structured test plan that a QA engineer can follow.
"""

        return prompt

    def generate_automated_test_code(
        self,
        test_scenarios: str,
        language: str = "python",
        framework: str = "pytest"
    ) -> str:
        """
        Generate actual test code from test scenarios.

        Args:
            test_scenarios: The test scenarios text
            language: Programming language for tests
            framework: Testing framework to use

        Returns:
            Generated test code
        """
        prompt = f"""Based on the following test scenarios, generate actual test code in {language} using {framework}.

Test Scenarios:
{test_scenarios}

Generate complete, runnable test code with:
- Proper imports and setup
- Well-named test functions
- Assertions and validations
- Comments explaining the tests
- Mock data where needed

Provide the code in a format ready to copy into a test file.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.5,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text
