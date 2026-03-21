"""
Excel Mapper Module
Uses Claude AI (via AWS Bedrock) to semantically map generated test cases
against existing test cases from an uploaded Excel file.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Confidence thresholds
THRESHOLD_MAPPED = 75          # ≥ 75% → MAPPED
THRESHOLD_POSSIBLE = 40        # 40–74% → POSSIBLE MATCH
                                # < 40% or no match → NOT IMPACTED


@dataclass
class MappingResult:
    """Result of mapping generated test cases against existing Excel test cases."""

    mappings: List[Dict] = field(default_factory=list)
    """
    One entry per Excel row:
    {
        excel_row_index: int,        # worksheet row number
        raw_id: str,                 # display identifier from Excel (TC ID or row num)
        generated_tc_id: str|None,   # best matching generated TC id, or None
        generated_title: str|None,   # title of that TC for display
        status: str,                 # MAPPED | POSSIBLE MATCH | NOT IMPACTED
        confidence: int,             # 0–100
        notes: str,                  # explanation from AI
    }
    """

    new_generated_ids: List[str] = field(default_factory=list)
    """IDs of generated test cases that did not match any Excel row."""

    stats: Dict = field(default_factory=dict)
    """
    {
        mapped: int,
        possible_match: int,
        not_covered: int,
        new_generated: int,
        total_excel: int,
        total_generated: int,
    }
    """


class ExcelMapper:
    """
    Semantically maps generated test cases against existing Excel test cases
    using Claude AI via AWS Bedrock.
    """

    MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.1   # deterministic — mapping should be consistent

    def __init__(self, bedrock_client):
        """
        Args:
            bedrock_client: A boto3 bedrock-runtime client instance.
        """
        self._client = bedrock_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def map(self, excel_rows: List[Dict], generated_cases: List[Dict]) -> MappingResult:
        """
        Map generated test cases to existing Excel rows.

        Args:
            excel_rows: Parsed rows from ExcelProcessor.parse().
            generated_cases: Structured test cases from TestScenarioGenerator.generate_structured_test_cases().

        Returns:
            MappingResult with per-row mappings, new_generated_ids, and stats.
        """
        if not excel_rows or not generated_cases:
            return self._empty_result(excel_rows, generated_cases)

        prompt = self._build_mapping_prompt(excel_rows, generated_cases)
        raw_response = self._invoke(prompt)
        ai_output = self._parse_ai_response(raw_response)

        return self._build_result(ai_output, excel_rows, generated_cases)

    # ------------------------------------------------------------------
    # Private: prompt construction
    # ------------------------------------------------------------------

    def _build_mapping_prompt(self, excel_rows: List[Dict], generated_cases: List[Dict]) -> str:
        # Compact serialisation of Excel rows (only meaningful fields)
        existing_list = []
        for row in excel_rows:
            existing_list.append({
                "row_index": row["row_index"],
                "raw_id": row.get("_raw_id", str(row["row_index"])),
                "scenario": row.get("test_scenario") or row.get("description") or row.get("test_case") or "",
                "steps": row.get("test_steps", ""),
                "expected": row.get("expected_result", ""),
            })

        # Compact serialisation of generated cases
        generated_list = []
        for tc in generated_cases:
            steps_text = " | ".join(tc.get("steps", [])) if isinstance(tc.get("steps"), list) else ""
            generated_list.append({
                "id": tc.get("id", ""),
                "title": tc.get("title", ""),
                "type": tc.get("type", ""),
                "category": tc.get("category", ""),
                "steps": steps_text,
                "expected": tc.get("expected_result", ""),
            })

        prompt = f"""You are a senior QA engineer performing test coverage analysis.

## Task
Map each EXISTING test case (from the Excel file) to the BEST matching GENERATED test case (from the PR analysis).
Rules:
1. Each existing row maps to AT MOST ONE generated test case (the best match).
2. If two generated test cases equally match the same existing row, pick the highest confidence one.
3. An existing row with no reasonable match gets confidence 0 and generated_tc_id null.
4. A generated test case not matched to any existing row will be identified as "new coverage".
5. Base matching on semantic similarity of the scenario description, test steps, and expected result — NOT on IDs.

## Confidence scoring guide
- 80–100: Near-identical scenario, steps, and expected outcome
- 60–79:  Same scenario, steps differ slightly or are more detailed
- 40–59:  Same general area/feature but different angle or partial overlap
- 20–39:  Loosely related, different focus
- 0–19:   No meaningful relationship

## Existing test cases (from Excel)
{json.dumps(existing_list, indent=2)}

## Generated test cases (from PR analysis)
{json.dumps(generated_list, indent=2)}

## Required output format
Return ONLY valid JSON — no markdown fences, no explanation. Schema:
{{
  "mappings": [
    {{
      "excel_row_index": <int>,
      "generated_tc_id": "<string or null>",
      "confidence": <0-100>,
      "notes": "<one sentence explanation>"
    }}
  ],
  "unmapped_generated_ids": ["TC-005", "TC-006"]
}}

- "mappings" must have exactly one entry per existing test case row.
- "unmapped_generated_ids" lists generated TC ids that were not chosen as the best match for any existing row.
"""
        return prompt

    # ------------------------------------------------------------------
    # Private: Bedrock invocation
    # ------------------------------------------------------------------

    def _invoke(self, prompt: str) -> str:
        response = self._client.invoke_model(
            modelId=self.MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.MAX_TOKENS,
                "temperature": self.TEMPERATURE,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )
        return json.loads(response["body"].read())["content"][0]["text"].strip()

    # ------------------------------------------------------------------
    # Private: response parsing
    # ------------------------------------------------------------------

    def _parse_ai_response(self, text: str) -> Dict:
        """Strip markdown fences if present and parse JSON."""
        if text.startswith("```"):
            first_newline = text.index("\n")
            last_fence = text.rfind("```")
            if last_fence > first_newline:
                text = text[first_newline + 1:last_fence].strip()
            else:
                text = text[first_newline + 1:].strip()
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("Failed to parse AI mapping response: %s", exc)
            return {"mappings": [], "unmapped_generated_ids": []}

    # ------------------------------------------------------------------
    # Private: result construction
    # ------------------------------------------------------------------

    def _build_result(
        self,
        ai_output: Dict,
        excel_rows: List[Dict],
        generated_cases: List[Dict],
    ) -> MappingResult:
        """Combine AI output with confidence thresholds to produce MappingResult."""

        generated_by_id: Dict[str, Dict] = {tc["id"]: tc for tc in generated_cases if tc.get("id")}

        # Index AI mappings by excel_row_index for O(1) lookup
        ai_by_row: Dict[int, Dict] = {}
        for m in ai_output.get("mappings", []):
            ai_by_row[m["excel_row_index"]] = m

        mappings: List[Dict] = []
        for row in excel_rows:
            row_idx = row["row_index"]
            ai_m = ai_by_row.get(row_idx, {})
            confidence = ai_m.get("confidence", 0) or 0
            tc_id = ai_m.get("generated_tc_id")

            # Apply confidence threshold
            if tc_id and confidence >= THRESHOLD_MAPPED:
                status = "MAPPED"
            elif tc_id and confidence >= THRESHOLD_POSSIBLE:
                status = "POSSIBLE MATCH"
            else:
                status = "NOT IMPACTED"
                tc_id = None  # don't show a TC id for unconfident matches

            tc = generated_by_id.get(tc_id or "") if tc_id else None
            mappings.append({
                "excel_row_index": row_idx,
                "raw_id": row.get("_raw_id", str(row_idx)),
                "generated_tc_id": tc_id,
                "generated_title": tc.get("title", "") if tc else "",
                "status": status,
                "confidence": confidence if tc_id else 0,
                "notes": ai_m.get("notes", ""),
            })

        # Determine NEW generated test cases
        matched_tc_ids = {m["generated_tc_id"] for m in mappings if m["generated_tc_id"]}
        unmapped_from_ai = set(ai_output.get("unmapped_generated_ids", []))
        # Union: any generated TC not matched to an existing row
        all_generated_ids = {tc.get("id", "") for tc in generated_cases}
        new_generated_ids = sorted(all_generated_ids - matched_tc_ids)

        # Stats
        status_counts = {"MAPPED": 0, "POSSIBLE MATCH": 0, "NOT IMPACTED": 0}
        for m in mappings:
            status_counts[m["status"]] = status_counts.get(m["status"], 0) + 1

        stats = {
            "mapped": status_counts["MAPPED"],
            "possible_match": status_counts["POSSIBLE MATCH"],
            "not_covered": status_counts["NOT IMPACTED"],
            "new_generated": len(new_generated_ids),
            "total_excel": len(excel_rows),
            "total_generated": len(generated_cases),
        }

        return MappingResult(
            mappings=mappings,
            new_generated_ids=new_generated_ids,
            stats=stats,
        )

    def _empty_result(self, excel_rows: List[Dict], generated_cases: List[Dict]) -> MappingResult:
        mappings = [
            {
                "excel_row_index": row["row_index"],
                "raw_id": row.get("_raw_id", str(row["row_index"])),
                "generated_tc_id": None,
                "generated_title": "",
                "status": "NOT IMPACTED",
                "confidence": 0,
                "notes": "No generated test cases to map against.",
            }
            for row in excel_rows
        ]
        return MappingResult(
            mappings=mappings,
            new_generated_ids=[tc.get("id", "") for tc in generated_cases],
            stats={
                "mapped": 0,
                "possible_match": 0,
                "not_covered": len(excel_rows),
                "new_generated": len(generated_cases),
                "total_excel": len(excel_rows),
                "total_generated": len(generated_cases),
            },
        )
