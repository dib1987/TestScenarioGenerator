"""
Decision Rules Module
Applies deterministic execution decisions to each mapping entry.

No AI calls, no I/O, no external dependencies.
Input:  one mapping dict (keys: status, confidence, ...)
Output: same dict with three keys added:
        execution_decision, execution_reason, suggested_action
"""


def apply_decision(mapping: dict) -> dict:
    """
    Enrich a single mapping dict with three decision fields.

    Decision logic is based only on:
      - status:     "MAPPED" | "POSSIBLE MATCH" | "NOT IMPACTED"
      - confidence: integer 0–100 (may be missing/None, treated as 0)

    Rules (evaluated top-to-bottom, first match wins):
      MAPPED + confidence >= 75  → RUN        | Reuse Existing Test
      MAPPED + confidence <  75  → REVIEW     | Manual Review
      POSSIBLE MATCH + conf >= 60 → REVIEW    | Update Existing Test
      POSSIBLE MATCH + conf <  60 → REVIEW    | Manual Review
      NOT IMPACTED (any)          → MUST_ADD_AND_RUN | Add New Test

    Args:
        mapping: A dict from MappingResult.mappings with at least 'status'
                 and 'confidence' keys.

    Returns:
        The same dict (mutated in-place) with three new keys.
    """
    status = mapping.get("status", "NOT IMPACTED")
    confidence = int(mapping.get("confidence") or 0)

    decision, reason, action = _decide(status, confidence)

    mapping["execution_decision"] = decision
    mapping["execution_reason"] = reason
    mapping["suggested_action"] = action
    return mapping


def _decide(status: str, confidence: int) -> tuple:
    """
    Core decision table. Returns (execution_decision, execution_reason, suggested_action).

    Kept as a separate function so it can be unit-tested independently
    without constructing a full mapping dict.
    """

    if status == "MAPPED":
        if confidence >= 75:
            # Strong or solid match — safe to include in regression run as-is
            return (
                "RUN",
                f"Strong match ({confidence}%) — existing test covers this scenario. Include in regression run.",
                "Reuse Existing Test",
            )
        else:
            # Mapped but confidence is low — something may have changed; human should check
            return (
                "REVIEW",
                f"Match confidence ({confidence}%) is below threshold. Manual review recommended before running.",
                "Manual Review",
            )

    if status == "POSSIBLE MATCH":
        if confidence >= 60:
            # Partial match with reasonable confidence — test probably needs a tweak
            return (
                "REVIEW",
                f"Partial match ({confidence}%) — test may need updating to cover the changed behaviour.",
                "Update Existing Test",
            )
        else:
            # Partial match with low confidence — not reliable enough to use without review
            return (
                "REVIEW",
                f"Low confidence partial match ({confidence}%). Manual review required.",
                "Manual Review",
            )

    # NOT IMPACTED — this existing test case is unrelated to the PR changes.
    # The PR did not touch this area, so there is no need to run it.
    return (
        "SKIP",
        "This test is not impacted by the PR changes. Safe to exclude from this regression run.",
        "No Action Required",
    )
