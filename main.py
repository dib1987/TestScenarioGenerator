"""
PR Test Scenario Generator - Main Entry Point
Automatically generates test scenarios from pull request code changes.
"""

import os
import sys
from dotenv import load_dotenv
from src.git_analyzer import GitAnalyzer, GitHubPRAnalyzer
from src.code_analyzer import CodeAnalyzer
from src.test_generator import TestScenarioGenerator


def main():
    """Main function to run the PR test scenario generator."""

    # Load environment variables
    load_dotenv()

    print("=" * 70)
    print("PR Test Scenario Generator")
    print("=" * 70)
    print()

    # Get user input for the source
    print("How would you like to provide the code changes?")
    print("1. Local git repository (compare branches)")
    print("2. GitHub pull request URL")
    print("3. Enter git diff manually")
    print()

    choice = input("Enter your choice (1-3): ").strip()
    print()

    diff_text = None
    pr_context = None

    try:
        if choice == "1":
            # Local git repository
            repo_path = input("Enter repository path (press Enter for current directory): ").strip() or "."
            base_branch = input("Enter base branch (e.g., 'main'): ").strip()
            compare_branch = input("Enter compare branch (e.g., 'feature/new-feature'): ").strip()

            print(f"\nAnalyzing changes between {base_branch} and {compare_branch}...")
            git_analyzer = GitAnalyzer(repo_path)
            diff_text = git_analyzer.get_diff_between_branches(base_branch, compare_branch)

            if not diff_text:
                print("No changes found between the branches.")
                return

        elif choice == "2":
            # GitHub PR
            pr_url = input("Enter GitHub PR URL (e.g., https://github.com/owner/repo/pull/123): ").strip()

            # Parse the URL
            parts = pr_url.split('/')
            if len(parts) < 7 or 'github.com' not in pr_url:
                print("Invalid GitHub PR URL format.")
                return

            owner = parts[-4]
            repo = parts[-3]
            pr_number = int(parts[-1])

            github_token = os.getenv("GITHUB_TOKEN")
            gh_analyzer = GitHubPRAnalyzer(github_token)

            print(f"\nFetching PR #{pr_number} from {owner}/{repo}...")
            diff_text = gh_analyzer.get_pr_diff(owner, repo, pr_number)
            pr_context = gh_analyzer.get_pr_info(owner, repo, pr_number)

            print(f"PR Title: {pr_context['title']}")
            print(f"Author: {pr_context['author']}")
            print()

        elif choice == "3":
            # Manual diff
            print("Paste your git diff (press Ctrl+D or Ctrl+Z when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            diff_text = '\n'.join(lines)

        else:
            print("Invalid choice.")
            return

        if not diff_text or not diff_text.strip():
            print("No diff content provided.")
            return

        # Analyze the code changes
        print("\nAnalyzing code changes...")
        code_analyzer = CodeAnalyzer()
        parsed_diff = code_analyzer.parse_diff(diff_text)
        change_types = code_analyzer.identify_change_types(parsed_diff)
        diff_summary = code_analyzer.generate_summary(parsed_diff)

        print(diff_summary)

        # Generate test scenarios
        print("\nGenerating test scenarios using Claude AI...")
        print("This may take a moment...\n")

        test_generator = TestScenarioGenerator()
        test_scenarios = test_generator.generate_test_scenarios(
            diff_summary=diff_summary,
            parsed_diff=parsed_diff,
            change_types=change_types,
            pr_context=pr_context
        )

        # Display results
        print("=" * 70)
        print("GENERATED TEST SCENARIOS")
        print("=" * 70)
        print()
        print(test_scenarios)
        print()

        # Ask if user wants to generate test code
        generate_code = input("\nWould you like to generate actual test code? (y/n): ").strip().lower()

        if generate_code == 'y':
            language = input("Enter programming language (default: python): ").strip() or "python"
            framework = input("Enter testing framework (default: pytest): ").strip() or "pytest"

            print("\nGenerating test code...")
            test_code = test_generator.generate_automated_test_code(
                test_scenarios=test_scenarios,
                language=language,
                framework=framework
            )

            print("\n" + "=" * 70)
            print("GENERATED TEST CODE")
            print("=" * 70)
            print()
            print(test_code)
            print()

        # Ask if user wants to save results
        save_results = input("\nWould you like to save the results to a file? (y/n): ").strip().lower()

        if save_results == 'y':
            filename = input("Enter filename (default: test_scenarios.md): ").strip() or "test_scenarios.md"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Generated Test Scenarios\n\n")
                f.write(diff_summary)
                f.write("\n\n")
                f.write(test_scenarios)

                if generate_code == 'y':
                    f.write("\n\n# Generated Test Code\n\n")
                    f.write(test_code)

            print(f"\nResults saved to {filename}")

        print("\nDone! Thank you for using PR Test Scenario Generator.")

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
