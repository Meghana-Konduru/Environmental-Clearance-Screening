
"""
Evidence-based preliminary classification for cement plant screening.

This module provides preliminary screening only.
It does not issue statutory environmental clearance decisions.
"""

from typing import Any, Dict, List


def classify_cement_project(
    project_details: Dict[str, Any],
    regulatory_context: List[Any],
) -> Dict[str, Any]:

    capacity = project_details.get(
        "project_capacity_million_tonnes_per_year"
    )
    distance = project_details.get("protected_area_distance_km")

    if capacity is None or distance is None:
        return _escalate("Capacity or protected-area distance is missing.")

    try:
        capacity = float(capacity)
        distance = float(distance)
    except (TypeError, ValueError):
        return _escalate("Capacity or distance is invalid.")

    if capacity <= 0 or distance < 0:
        return _escalate("Capacity or distance is outside the valid range.")

    # Support both LangChain Document objects and dictionaries.
    evidence = []

    for item in regulatory_context:
        if isinstance(item, dict):
            metadata = item.get("metadata", item)
            content = item.get(
                "page_content",
                item.get("content", "")
            )
        else:
            metadata = getattr(item, "metadata", {})
            content = getattr(item, "page_content", "")

        evidence.append({
            "metadata": metadata,
            "content": content,
        })

    schedule_matches = [
        item for item in evidence
        if item["metadata"].get("document_name")
        == "eia_notification_2006_consolidated.pdf"
        and str(item["metadata"].get("page_number")) == "22"
        and "3(b)" in item["content"]
        and "Cement plants" in item["content"]
    ]

    condition_matches = [
        item for item in evidence
        if item["metadata"].get("document_name")
        == "eia_notification_2006_consolidated.pdf"
        and str(item["metadata"].get("page_number")) == "30"
        and "5 km" in item["content"]
    ]

    if not schedule_matches or not condition_matches:
        return _escalate(
            "Required Schedule or General Condition evidence was not retrieved."
        )

    all_matches = schedule_matches + condition_matches

    citations = [
        {
            "document_name": item["metadata"].get("document_name"),
            "source_file": item["metadata"].get("source_file"),
            "page_number": item["metadata"].get("page_number"),
            "applicability_status": item["metadata"].get(
                "applicability_status"
            ),
            "retrieved_text": item["content"],
        }
        for item in all_matches
    ]

    # Require verified evidence before classification.
    if any(
        item["metadata"].get("applicability_status") != "verified_current"
        for item in all_matches
    ):
        return {
            "status": "escalated",
            "reason": "Regulatory evidence is pending verification.",
            "category": None,
            "routing": "human_review",
            "citations": citations,
        }

    # The Schedule threshold for cement plants.
    schedule_category = "A" if capacity >= 1.0 else "B"

    # Do not automatically apply the General Condition.
    # Its exceptions and project applicability need verification.
    if schedule_category == "B" and distance <= 5:
        return {
            "status": "escalated",
            "reason": (
                "The project may attract the General Condition. "
                "Verify Protected Area notification, applicable "
                "exceptions and the complete current provision."
            ),
            "category": None,
            "routing": "human_review",
            "citations": citations,
        }

    return {
        "status": "preliminary_opinion",
        "schedule_item": "3(b)",
        "schedule_category": schedule_category,
        "final_category": schedule_category,
        "routing": (
            "central_ministry"
            if schedule_category == "A"
            else "state_authority"
        ),
        "citations": citations,
        "disclaimer": (
            "Preliminary screening opinion only. "
            "Not an environmental clearance decision."
        ),
    }


def _escalate(reason: str) -> Dict[str, Any]:
    return {
        "status": "escalated",
        "reason": reason,
        "category": None,
        "routing": "human_review",
        "citations": [],
    }
