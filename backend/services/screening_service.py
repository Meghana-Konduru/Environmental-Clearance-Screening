
import re

from agents.graph import run_screening
from agents.classification import classify_cement_project
from rag.retriever import RegulatoryRetriever


def extract_number(value, unit_pattern):
    """Extract a number only when the expected unit is present."""

    if not isinstance(value, str):
        return None

    match = re.search(
        rf"(\d+(?:\.\d+)?)\s*{unit_pattern}",
        value,
        re.IGNORECASE,
    )

    return float(match.group(1)) if match else None


def perform_screening(project_details: dict):

    try:
        # Step 1: Run the existing LangGraph workflow.
        result = run_screening(project_details)

        # Step 2: Apply the cement-specific classifier only
        # to cement plant projects.
        project_type = str(
            project_details.get("project_type", "")
        ).lower()

        if "cement" not in project_type:
            result["classification_result"] = {
                "status": "not_applicable",
                "reason": "The current classification module supports cement plants only.",
            }

            return {
                "success": True,
                "data": result,
            }

        # Step 3: Retrieve the relevant Schedule evidence.
        retriever = RegulatoryRetriever()

        schedule_docs = retriever.search(
            query="Schedule item 3(b) Cement plants production capacity Category A Category B",
            k=3,
            include_withdrawn=False,
        )

        # Step 4: Retrieve General Condition evidence separately.
        condition_docs = retriever.search(
            query="General Condition Category B project within 5 km Protected Areas Wildlife Protection Act exceptions",
            k=5,
            include_withdrawn=False,
        )

        # Step 5: Convert LangChain documents into the
        # dictionary format expected by classification.py.
        regulatory_context = []

        for document in schedule_docs + condition_docs:
            metadata = document.metadata

            regulatory_context.append({
                "content": document.page_content,
                "document_name": metadata.get("document_name"),
                "source_file": metadata.get("source_file"),
                "page_number": metadata.get("page_number"),
                "applicability_status": metadata.get(
                    "applicability_status",
                    "pending_verification",
                ),
            })

        # Step 6: Extract capacity and distance from project details.
        capacity = extract_number(
            project_details.get("project_capacity"),
            r"million\s+tonnes(?:\s*/\s*annum|\s+per\s+year)?",
        )

        distance = extract_number(
            project_details.get("protected_area_proximity"),
            r"km",
        )

        classification_input = {
            "project_capacity_million_tonnes_per_year": capacity,
            "protected_area_distance_km": distance,
        }

        # Step 7: Execute your classification module.
        classification_result = classify_cement_project(
            classification_input,
            regulatory_context,
        )

        # Step 8: Add classification and evidence to the
        # existing LangGraph result without changing its nodes.
        result["classification_result"] = classification_result
        result["classification_regulatory_context"] = regulatory_context

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
