"""
Code Analyzer Module
Analyzes code changes from git diffs to understand what was modified.
"""

from typing import Dict, List
import re


class CodeAnalyzer:
    """Analyzes code diffs to extract meaningful change information."""

    def __init__(self):
        """Initialize the Code Analyzer."""
        pass

    def parse_diff(self, diff_text: str) -> List[Dict]:
        """
        Parse a git diff into structured information.

        Args:
            diff_text: Raw git diff text

        Returns:
            List of dictionaries containing file changes
        """
        files_changed = []
        current_file = None

        for line in diff_text.split('\n'):
            # New file marker
            if line.startswith('diff --git'):
                if current_file:
                    files_changed.append(current_file)

                # Extract file paths
                match = re.search(r'a/(.*?) b/(.*?)$', line)
                if match:
                    current_file = {
                        'file_path': match.group(2),
                        'additions': [],
                        'deletions': [],
                        'context': []
                    }

            # Track additions
            elif line.startswith('+') and not line.startswith('+++'):
                if current_file:
                    current_file['additions'].append(line[1:])

            # Track deletions
            elif line.startswith('-') and not line.startswith('---'):
                if current_file:
                    current_file['deletions'].append(line[1:])

            # Track context
            elif current_file and line.startswith(' '):
                current_file['context'].append(line[1:])

        # Add the last file
        if current_file:
            files_changed.append(current_file)

        return files_changed

    def identify_change_types(self, parsed_diff: List[Dict]) -> Dict[str, List[str]]:
        """
        Identify types of changes made in the diff.

        Args:
            parsed_diff: Parsed diff from parse_diff()

        Returns:
            Dictionary categorizing changes by type
        """
        change_types = {
            'new_functions': [],
            'modified_functions': [],
            'deleted_functions': [],
            'new_classes': [],
            'modified_classes': [],
            'api_changes': [],
            'database_changes': [],
            'config_changes': []
        }

        for file_change in parsed_diff:
            file_path = file_change['file_path']
            additions = file_change['additions']
            deletions = file_change['deletions']

            # Detect function additions
            for line in additions:
                if self._is_function_declaration(line):
                    change_types['new_functions'].append(f"{file_path}: {line.strip()}")
                elif self._is_class_declaration(line):
                    change_types['new_classes'].append(f"{file_path}: {line.strip()}")
                elif self._is_api_endpoint(line):
                    change_types['api_changes'].append(f"{file_path}: {line.strip()}")

            # Detect configuration changes
            if self._is_config_file(file_path):
                change_types['config_changes'].append(file_path)

            # Detect database changes
            if self._is_database_file(file_path):
                change_types['database_changes'].append(file_path)

        return change_types

    def _is_function_declaration(self, line: str) -> bool:
        """Check if a line is a function declaration."""
        patterns = [
            r'^\s*def\s+\w+\s*\(',  # Python
            r'^\s*function\s+\w+\s*\(',  # JavaScript
            r'^\s*const\s+\w+\s*=\s*\(.*\)\s*=>',  # Arrow functions
            r'^\s*(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(',  # Java/C#
        ]
        return any(re.search(pattern, line) for pattern in patterns)

    def _is_class_declaration(self, line: str) -> bool:
        """Check if a line is a class declaration."""
        patterns = [
            r'^\s*class\s+\w+',  # Most languages
            r'^\s*(public|private)?\s*class\s+\w+',  # Java/C#
        ]
        return any(re.search(pattern, line) for pattern in patterns)

    def _is_api_endpoint(self, line: str) -> bool:
        """Check if a line defines an API endpoint."""
        patterns = [
            r'@app\.(get|post|put|delete|patch)',  # Flask/FastAPI
            r'@(Get|Post|Put|Delete|Patch)Mapping',  # Spring
            r'router\.(get|post|put|delete|patch)',  # Express
        ]
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns)

    def _is_config_file(self, file_path: str) -> bool:
        """Check if a file is a configuration file."""
        config_patterns = ['.yml', '.yaml', '.json', '.env', '.config', '.ini', '.toml']
        return any(file_path.endswith(pattern) for pattern in config_patterns)

    def _is_database_file(self, file_path: str) -> bool:
        """Check if a file is related to database changes."""
        db_patterns = ['migration', 'schema', 'model', 'entity', 'repository']
        return any(pattern in file_path.lower() for pattern in db_patterns)

    def generate_summary(self, parsed_diff: List[Dict]) -> str:
        """
        Generate a human-readable summary of changes.

        Args:
            parsed_diff: Parsed diff from parse_diff()

        Returns:
            Summary string
        """
        total_files = len(parsed_diff)
        total_additions = sum(len(f['additions']) for f in parsed_diff)
        total_deletions = sum(len(f['deletions']) for f in parsed_diff)

        summary = f"Changes Summary:\n"
        summary += f"- Files changed: {total_files}\n"
        summary += f"- Lines added: {total_additions}\n"
        summary += f"- Lines deleted: {total_deletions}\n\n"
        summary += "Modified files:\n"

        for file_change in parsed_diff:
            file_path = file_change['file_path']
            adds = len(file_change['additions'])
            dels = len(file_change['deletions'])
            summary += f"  - {file_path} (+{adds}, -{dels})\n"

        return summary
