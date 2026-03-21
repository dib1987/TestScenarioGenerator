"""
Jira + Zephyr Scale Client — Phase 2 Scaffold
Authentication: Jira API Token (Bearer).
Hierarchy: Test cases live under a User Story (issue link).

Activate by setting JIRA_BASE_URL, JIRA_API_TOKEN, and JIRA_PROJECT_KEY in .env.
All write/fetch methods raise NotImplementedError until Phase 2 is implemented.
Only health_check() is live so the UI can show connection status.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared schema — aligns with Zephyr Scale test case fields
# and mirrors ExcelProcessor canonical column names.
# ---------------------------------------------------------------------------

@dataclass
class ZephyrTestCase:
    """
    Canonical test case schema shared between Excel import and Zephyr Scale.

    Field mapping:
        summary        ← Excel "Test Case" / Zephyr Scale "Summary"
        description    ← Excel "Description" / Zephyr Scale "Description"
        precondition   ← Excel "Precondition" / Zephyr Scale "Precondition"
        test_steps     ← Excel "Test Steps" / Zephyr Scale "Test Steps"
        expected_result← Excel "Expected Result" / Zephyr Scale "Expected Result"
    """
    id: str = ""
    summary: str = ""           # ← Test Case / Zephyr Summary
    description: str = ""       # ← Description
    precondition: str = ""      # ← Precondition
    test_steps: List[str] = field(default_factory=list)    # ← Test Steps (list)
    expected_result: str = ""   # ← Expected Result
    status: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    story_id: Optional[str] = None   # Linked Jira User Story key (e.g. "PROJ-123")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class ZephyrScaleClient:
    """
    Jira + Zephyr Scale REST API client.

    Usage:
        client = ZephyrScaleClient.from_env()
        if client and client.health_check():
            # connection is valid
    """

    def __init__(self, base_url: str, api_token: str, project_key: str):
        """
        Args:
            base_url:     Jira base URL, e.g. "https://your-org.atlassian.net"
            api_token:    Jira API token (from id.atlassian.com/manage-profile/security/api-tokens)
            project_key:  Jira project key, e.g. "PROJ"
        """
        self.base_url = base_url.rstrip("/")
        self.project_key = project_key
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> Optional["ZephyrScaleClient"]:
        """
        Create a client from environment variables.
        Returns None if JIRA_BASE_URL is not set (Jira integration disabled).
        """
        base_url = os.getenv("JIRA_BASE_URL", "").strip()
        api_token = os.getenv("JIRA_API_TOKEN", "").strip()
        project_key = os.getenv("JIRA_PROJECT_KEY", "").strip()

        if not base_url:
            return None
        if not api_token:
            logger.warning("JIRA_BASE_URL is set but JIRA_API_TOKEN is missing.")
            return None

        return cls(base_url=base_url, api_token=api_token, project_key=project_key)

    # ------------------------------------------------------------------
    # Health check (LIVE — used by /api/jira/health)
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify Jira connectivity and token validity by calling /rest/api/3/myself.

        Returns:
            True if the credentials are valid and Jira is reachable.
        """
        try:
            resp = self._session.get(
                f"{self.base_url}/rest/api/3/myself",
                timeout=5,
            )
            return resp.status_code == 200
        except requests.RequestException as exc:
            logger.warning("Jira health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Phase 2 stubs — fetch
    # ------------------------------------------------------------------

    def get_test_cases_for_story(self, story_id: str) -> List[ZephyrTestCase]:
        """
        Fetch all Zephyr Scale test cases linked to a Jira User Story.

        Args:
            story_id: Jira issue key, e.g. "PROJ-123"

        Returns:
            List of ZephyrTestCase objects.

        Raises:
            NotImplementedError: Phase 2 — not yet implemented.
        """
        raise NotImplementedError(
            "Zephyr Scale test case fetch is Phase 2. "
            "Use Excel upload for mapping in the meantime."
        )

    def get_test_cycle(self, cycle_id: str) -> dict:
        """
        Fetch a Zephyr Scale test cycle by ID.

        Raises:
            NotImplementedError: Phase 2 — not yet implemented.
        """
        raise NotImplementedError("Zephyr Scale API integration — Phase 2")

    # ------------------------------------------------------------------
    # Phase 2 stubs — write
    # ------------------------------------------------------------------

    def create_test_case(self, test_case: ZephyrTestCase, story_id: str) -> str:
        """
        Create a new test case in Zephyr Scale linked to a User Story.

        Args:
            test_case: Populated ZephyrTestCase object.
            story_id:  Jira User Story key to link the test case to.

        Returns:
            The Zephyr Scale test case ID (string).

        Raises:
            NotImplementedError: Phase 2 — not yet implemented.
        """
        raise NotImplementedError("Zephyr Scale API integration — Phase 2")

    def update_test_case(self, tc_id: str, test_case: ZephyrTestCase) -> None:
        """
        Update an existing Zephyr Scale test case.

        Args:
            tc_id:     Zephyr Scale test case ID.
            test_case: Updated ZephyrTestCase object.

        Raises:
            NotImplementedError: Phase 2 — not yet implemented.
        """
        raise NotImplementedError("Zephyr Scale API integration — Phase 2")

    def bulk_create_test_cases(
        self, test_cases: List[ZephyrTestCase], story_id: str
    ) -> List[str]:
        """
        Bulk-create multiple test cases in Zephyr Scale under a User Story.

        Returns:
            List of created Zephyr Scale test case IDs.

        Raises:
            NotImplementedError: Phase 2 — not yet implemented.
        """
        raise NotImplementedError("Zephyr Scale API integration — Phase 2")
