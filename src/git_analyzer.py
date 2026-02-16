"""
Git Analyzer Module
Handles git operations and extracts diff information from pull requests.
"""

import git
from typing import Dict, List
import requests
import os


class GitAnalyzer:
    """Analyzes git repositories and extracts diff information."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize the Git Analyzer.

        Args:
            repo_path: Path to the git repository (default: current directory)
        """
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"'{repo_path}' is not a valid git repository")

    def get_diff_between_branches(self, base_branch: str, compare_branch: str) -> str:
        """
        Get the diff between two branches.

        Args:
            base_branch: The base branch (e.g., 'main')
            compare_branch: The branch to compare (e.g., 'feature/new-feature')

        Returns:
            String containing the diff
        """
        try:
            diff = self.repo.git.diff(base_branch, compare_branch)
            return diff
        except git.GitCommandError as e:
            raise ValueError(f"Error getting diff: {str(e)}")

    def get_diff_from_commits(self, commit1: str, commit2: str) -> str:
        """
        Get the diff between two commits.

        Args:
            commit1: First commit hash
            commit2: Second commit hash

        Returns:
            String containing the diff
        """
        try:
            diff = self.repo.git.diff(commit1, commit2)
            return diff
        except git.GitCommandError as e:
            raise ValueError(f"Error getting diff: {str(e)}")

    def get_changed_files(self, base_branch: str, compare_branch: str) -> List[str]:
        """
        Get list of files changed between branches.

        Args:
            base_branch: The base branch
            compare_branch: The branch to compare

        Returns:
            List of changed file paths
        """
        try:
            diff_index = self.repo.git.diff(base_branch, compare_branch, name_only=True)
            return diff_index.split('\n') if diff_index else []
        except git.GitCommandError as e:
            raise ValueError(f"Error getting changed files: {str(e)}")


class GitHubPRAnalyzer:
    """Analyzes GitHub pull requests using the GitHub API."""

    def __init__(self, token: str = None):
        """
        Initialize GitHub PR Analyzer.

        Args:
            token: GitHub personal access token (optional, but recommended for private repos)
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Get the diff for a specific pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number

        Returns:
            String containing the PR diff
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            raise ValueError(f"Error fetching PR: {response.status_code} - {response.text}")

    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict:
        """
        Get information about a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Dictionary containing PR information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return {
                "title": data["title"],
                "description": data["body"],
                "base_branch": data["base"]["ref"],
                "head_branch": data["head"]["ref"],
                "author": data["user"]["login"],
                "state": data["state"]
            }
        else:
            raise ValueError(f"Error fetching PR info: {response.status_code}")
