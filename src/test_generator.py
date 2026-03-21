"""
Test Generator Module
Uses Claude AI (via AWS Bedrock) to generate structured test scenarios directly from code changes.
Single Bedrock call per analysis — no intermediate markdown step.
"""

import boto3
import json
import os
from typing import Dict, List


class TestScenarioGenerator:
    """Generates structured test scenarios using Claude AI."""

    def __init__(self, model: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        )
        self.model = model

    def generate_structured_test_cases(
        self,
        diff_summary: str,
        parsed_diff: List[Dict],
        change_types: Dict[str, List[str]],
        pr_context: Dict = None,
    ) -> list:
        """
        Generate structured test cases directly from code change data.

        Single Bedrock call — returns a JSON list without an intermediate markdown step.

        Args:
            diff_summary:  Human-readable summary of changes.
            parsed_diff:   Structured diff (files, additions, deletions).
            change_types:  Categorised change types from CodeAnalyzer.
            pr_context:    Optional PR metadata (title, description, etc.).

        Returns:
            List of test case dicts, or [] on parse failure.
            Each dict: {id, title, type, priority, category, steps[], expected_result}
        """
        prompt = self._build_structured_prompt(diff_summary, parsed_diff, change_types, pr_context)

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )

        text = json.loads(response["body"].read())["content"][0]["text"].strip()

        # Strip markdown code fences if Claude wrapped the JSON
        if text.startswith("```"):
            first_newline = text.index("\n")
            last_fence = text.rfind("```")
            text = text[first_newline + 1: last_fence].strip() if last_fence > first_newline else text[first_newline + 1:].strip()

        try:
            result = json.loads(text)
            return result if isinstance(result, list) else []
        except (json.JSONDecodeError, ValueError):
            return []

    def _build_structured_prompt(
        self,
        diff_summary: str,
        parsed_diff: List[Dict],
        change_types: Dict[str, List[str]],
        pr_context: Dict = None,
    ) -> str:
        """Build the single prompt that produces structured test cases directly."""

        prompt = "You are a senior QA engineer. Analyse the following code changes and return a structured JSON array of test cases.\n\n"

        prompt += "## Code Changes Summary\n"
        prompt += diff_summary + "\n\n"

        if pr_context:
            prompt += "## Pull Request Context\n"
            prompt += f"Title: {pr_context.get('title', 'N/A')}\n"
            prompt += f"Description: {pr_context.get('description', 'N/A')}\n\n"

        prompt += "## Types of Changes Detected\n"
        for change_type, changes in change_types.items():
            if changes:
                prompt += f"\n### {change_type.replace('_', ' ').title()}\n"
                for change in changes:
                    prompt += f"- {change}\n"

        prompt += "\n## Detailed File Changes\n"
        for file_change in parsed_diff[:5]:
            prompt += f"\n### File: {file_change['file_path']}\n"
            prompt += f"Additions: {len(file_change['additions'])} lines | Deletions: {len(file_change['deletions'])} lines\n"
            if file_change["additions"]:
                prompt += "Key additions:\n"
                for line in file_change["additions"][:10]:
                    if line.strip():
                        prompt += f"  + {line}\n"

        prompt += """

## Output Requirements

Return ONLY a valid JSON array — no markdown fences, no explanation, no surrounding text.

Each element must follow this exact schema:
[
  {
    "id": "TC-001",
    "title": "Short descriptive title (max 10 words)",
    "type": "functional",
    "priority": "high",
    "category": "Category (e.g. Payment, Authentication, Product, Checkout)",
    "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
    "expected_result": "What the user or system should observe when the test passes"
  }
]

Rules:
- Include ONLY these three test types: functional, regression, e2e
- "priority" must be: high, medium, or low
- "steps" must have at least 2 items
- CRITICAL — Steps must be written in plain business language:
    Good: "Navigate to the checkout page and enter valid payment details, then confirm the order."
    Bad:  "Call PaymentService.processPayment() with a valid PaymentDTO object."
  Do NOT mention method names, class names, function calls, API routes, database queries, or any code-level detail.
  Describe what a user does or what the system does from a user/business perspective.
- Generate enough test cases to provide meaningful coverage of all detected changes
- Cover happy paths, negative paths, and boundary conditions across functional, regression, and e2e types
"""
        return prompt

    def generate_automated_test_code(
        self,
        structured_test_cases: list,
        language: str = "python",
        framework: str = "pytest",
    ) -> str:
        """
        Generate runnable test code from structured test cases.

        Args:
            structured_test_cases: List of test case dicts from generate_structured_test_cases().
            language:  Target programming language (default: python).
            framework: Test framework (default: pytest).

        Returns:
            Generated test code as a string.
        """
        cases_json = json.dumps(structured_test_cases, indent=2)

        prompt = f"""Based on the following structured test cases, generate actual {language} test code using {framework}.

Test Cases:
{cases_json}

Generate complete, runnable test code with:
- Proper imports and setup
- One test function per test case, named after the test case title
- Assertions and validations matching the expected results
- Comments explaining the business intent of each test
- Mock data and fixtures where needed

Provide the code ready to copy into a test file."""

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.5,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )

        return json.loads(response["body"].read())["content"][0]["text"]
