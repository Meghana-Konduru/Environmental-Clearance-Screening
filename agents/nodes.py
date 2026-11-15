
"""
Processing nodes for the Environmental Clearance
Pre-Screening LangGraph workflow.

This implementation uses deterministic Python logic
and the existing RAG retriever. It does not make AI-generated
legal or environmental determinations.
"""

from typing import Any, Dict, List

from agents.state import ScreeningState
from rag.retriever import RegulatoryRetriever


# Basic project fields needed for preliminary screening.
REQUIRED_PROJECT_FIELDS = [
    "project_type",
    "project_location",
    "proposed_activity",
    "project_capacity",
]


# Values that indicate information has not actually been supplied.
PLACEHOLDER_VALUES = {
    "",
    "not specified",
    "not yet specified",
    "not provided",
    "not available",
    "unknown",
    "n/a",
    "na",
    "none",
    "null",
    "nil",
    "tbd",
    "to be decided",
    "to be confirmed",
    "pending",
}


def _is_missing_value(value: Any) -> bool:
    """Check whether a value is empty or a placeholder."""

    if value is None:
        return True

    if isinstance(value, str):
        return value.strip().lower() in PLACEHOLDER_VALUES

    if isinstance(value, (list, dict)):
        return len(value) == 0

    return False


def _add_error(state: ScreeningState, message: str) -> List[str]:
    """Return existing errors with one additional error."""

    errors = list(state.get("errors", []))
    errors.append(message)
    return errors


def _get_project_text(project_details: Dict[str, Any]) -> str:
    """Convert non-placeholder project details into searchable text."""

    parts = []

    for key, value in project_details.items():
        if not _is_missing_value(value):
            parts.append(f"{key}: {value}")

    return " ".join(parts)


def _build_regulatory_query(
    project_details: Dict[str, Any],
) -> str:
    """
    Build a focused query for environmental regulation retrieval.

    Prioritises project type, activity, location and capacity.
    Additional environmental details are included when available.
    """

    query_parts = []

    important_fields = [
        ("Project type", "project_type"),
        ("Proposed activity", "proposed_activity"),
        ("Project location", "project_location"),
        ("Project capacity", "project_capacity"),
    ]

    for label, field in important_fields:
        value = project_details.get(field)

        if not _is_missing_value(value):
            query_parts.append(f"{label}: {value}")

    additional_fields = [
        "industry_type",
        "land_requirement",
        "water_usage",
        "water_source",
        "waste_generation",
        "wastewater_generation",
        "emissions",
        "fuel_requirement",
        "forest_land",
        "wildlife_proximity",
        "protected_area_proximity",
        "environmental_sensitivity",
    ]

    for field in additional_fields:
        value = project_details.get(field)

        if not _is_missing_value(value):
            query_parts.append(f"{field.replace('_', ' ')}: {value}")

    query_parts.append(
        "Environmental clearance under the EIA Notification 2006, "
        "relevant project Schedule entry, project category, "
        "appraisal authority and applicable regulatory conditions."
    )

    return " ".join(query_parts)


def screening_node(state: ScreeningState) -> Dict[str, Any]:
    """
    Examine project information and identify missing fields.

    Does not make a legal clearance determination.
    """

    project_details = state.get("project_details", {})

    if not isinstance(project_details, dict):
        return {
            "screening_result": {
                "project_details": {},
                "missing_information": REQUIRED_PROJECT_FIELDS,
                "preliminary_screening_observations": [
                    "Project details must be provided as a dictionary."
                ],
            },
            "current_step": "screening_completed",
            "errors": _add_error(
                state,
                "Invalid project_details format.",
            ),
        }

    missing_information = []

    for field in REQUIRED_PROJECT_FIELDS:
        value = project_details.get(field)

        if _is_missing_value(value):
            missing_information.append(field)

    observations = []

    if missing_information:
        observations.append(
            "Some required project information is missing or "
            "has only been provided as a placeholder."
        )
    else:
        observations.append(
            "The basic project information fields have been provided."
        )

    observations.append(
        "This is an initial information check, not a statutory "
        "environmental clearance decision."
    )

    screening_result = {
        "project_type": project_details.get(
            "project_type", "Not provided"
        ),
        "project_location": project_details.get(
            "project_location", "Not provided"
        ),
        "proposed_activity": project_details.get(
            "proposed_activity", "Not provided"
        ),
        "project_capacity": project_details.get(
            "project_capacity", "Not provided"
        ),
        "key_project_details": project_details,
        "missing_information": missing_information,
        "preliminary_screening_observations": observations,
    }

    return {
        "screening_result": screening_result,
        "current_step": "screening_completed",
    }


def regulatory_node(state: ScreeningState) -> Dict[str, Any]:
    """
    Retrieve relevant regulatory passages using the existing RAG system.

    Withdrawn historical documents are excluded by default.
    """

    project_details = state.get("project_details", {})

    if not isinstance(project_details, dict) or not project_details:
        return {
            "regulatory_context": [],
            "current_step": "regulatory_retrieval_completed",
            "errors": _add_error(
                state,
                "Regulatory retrieval skipped: project details are missing.",
            ),
        }

    query = _build_regulatory_query(project_details)

    if not query.strip():
        return {
            "regulatory_context": [],
            "current_step": "regulatory_retrieval_completed",
            "errors": _add_error(
                state,
                "Regulatory retrieval skipped: no searchable project details.",
            ),
        }

    try:
        retriever = RegulatoryRetriever()

        documents = retriever.search(
            query=query,
            k=5,
            include_withdrawn=False,
        )

        regulatory_context = []

        for document in documents:
            metadata = document.metadata

            regulatory_context.append({
                "content": document.page_content,
                "document_name": metadata.get(
                    "document_name", "Unknown"
                ),
                "document_id": metadata.get(
                    "document_id", "Unknown"
                ),
                "page_number": metadata.get(
                    "page_number", "Unknown"
                ),
                "document_type": metadata.get(
                    "document_type", "Unknown"
                ),
                "applicability_status": metadata.get(
                    "applicability_status",
                    "pending_verification",
                ),
                "similarity_distance": metadata.get(
                    "similarity_distance"
                ),
            })

        return {
            "regulatory_context": regulatory_context,
            "current_step": "regulatory_retrieval_completed",
        }

    except Exception as exc:
        return {
            "regulatory_context": [],
            "current_step": "regulatory_retrieval_failed",
            "errors": _add_error(
                state,
                f"Regulatory retrieval failed: {str(exc)}",
            ),
        }


def risk_node(state: ScreeningState) -> Dict[str, Any]:
    """
    Identify information topics that may need further environmental review.

    This baseline does not determine actual environmental risks.
    """

    project_details = state.get("project_details", {})
    project_text = _get_project_text(project_details).lower()

    review_keywords = {
        "forest and land use": [
            "forest",
            "forestland",
            "land diversion",
        ],
        "wildlife and biodiversity": [
            "wildlife",
            "sanctuary",
            "national park",
            "biodiversity",
        ],
        "water resources": [
            "water",
            "river",
            "groundwater",
            "effluent",
        ],
        "air quality and emissions": [
            "emission",
            "air pollution",
            "stack",
        ],
        "noise pollution": [
            "noise",
            "sound",
            "vibration",
        ],
        "waste management": [
            "waste",
            "hazardous waste",
            "solid waste",
        ],
    }

    topics_for_review = []

    for topic, keywords in review_keywords.items():
        if any(keyword in project_text for keyword in keywords):
            topics_for_review.append(topic)

    risk_assessment = {
        "identified_risks": [],
        "potential_risks": [],
        "topics_for_review": topics_for_review,
        "risk_explanations": [
            "The listed topics are indicators found in the supplied "
            "project description. They are not confirmed environmental risks."
        ],
        "further_information_required": [
            "Detailed project characteristics and technical specifications",
            "Site-specific environmental information",
            "Relevant environmental baseline studies, where required",
        ],
        "assessment_status": "preliminary_keyword_review_only",
    }

    return {
        "risk_assessment": risk_assessment,
        "current_step": "risk_review_completed",
    }


def report_node(state: ScreeningState) -> Dict[str, Any]:
    """
    Combine preceding node outputs into a structured preliminary report.
    """

    project_details = state.get("project_details", {})
    screening_result = state.get("screening_result", {})
    regulatory_context = state.get("regulatory_context", [])
    risk_assessment = state.get("risk_assessment", {})

    source_references = []

    for item in regulatory_context:
        source_references.append({
            "document_name": item.get("document_name", "Unknown"),
            "page_number": item.get("page_number", "Unknown"),
            "applicability_status": item.get(
                "applicability_status",
                "pending_verification",
            ),
        })

    missing_information = screening_result.get(
        "missing_information", []
    )

    recommended_next_steps = []

    if missing_information:
        recommended_next_steps.append(
            "Provide the missing project information: "
            + ", ".join(missing_information)
            + "."
        )

    recommended_next_steps.extend([
        "Review the retrieved regulatory provisions against "
        "authoritative current sources.",
        "Obtain further environmental studies or expert review "
        "where required.",
    ])

    final_report = {
        "report_title": "Environmental Clearance Preliminary Screening Report",
        "project_overview": project_details,
        "preliminary_screening_observations": screening_result,
        "relevant_regulatory_information": regulatory_context,
        "potential_environmental_risks": risk_assessment,
        "missing_information": missing_information,
        "recommended_next_steps": recommended_next_steps,
        "regulatory_source_references": source_references,
        "limitations": [
            "This is a preliminary screening output only.",
            "Retrieved documents marked pending_verification have "
            "not been confirmed as currently applicable.",
            "The output does not constitute statutory appraisal "
            "or environmental clearance approval.",
            "No final legal or environmental risk determination "
            "has been made.",
        ],
    }

    return {
        "final_report": final_report,
        "current_step": "report_completed",
    }
