
"""Interface for the preliminary environmental screening report agent."""

from typing import Any, Dict, List

from agents.nodes import report_node
from agents.state import ScreeningState


def run_report_agent(
    project_details: Dict[str, Any],
    screening_result: Dict[str, Any],
    regulatory_context: List[Dict[str, Any]],
    risk_assessment: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a preliminary report from the available agent outputs."""

    if not isinstance(project_details, dict):
        raise TypeError("project_details must be a dictionary.")

    if not isinstance(screening_result, dict):
        raise TypeError("screening_result must be a dictionary.")

    if not isinstance(regulatory_context, list):
        raise TypeError("regulatory_context must be a list.")

    if not isinstance(risk_assessment, dict):
        raise TypeError("risk_assessment must be a dictionary.")

    state: ScreeningState = {
        "project_details": project_details,
        "screening_result": screening_result,
        "regulatory_context": regulatory_context,
        "risk_assessment": risk_assessment,
        "errors": [],
    }

    result = report_node(state)

    return result.get("final_report", {})


if __name__ == "__main__":
    sample_project = {
        "project_type": "Industrial project",
        "project_location": "Example industrial area, Karnataka",
        "proposed_activity": "Manufacturing facility",
        "project_capacity": "Not yet specified",
    }

    sample_screening = {
        "missing_information": ["Project capacity needs confirmation"],
        "preliminary_screening_observations": [
            "Basic project information requires review."
        ],
    }

    sample_regulatory_context = []

    sample_risk_assessment = {
        "identified_risks": [],
        "potential_risks": [],
        "topics_for_review": ["Water resources", "Waste management"],
        "assessment_status": "preliminary_keyword_review_only",
    }

    report = run_report_agent(
        project_details=sample_project,
        screening_result=sample_screening,
        regulatory_context=sample_regulatory_context,
        risk_assessment=sample_risk_assessment,
    )

    print("\nPRELIMINARY SCREENING REPORT AGENT")
    print("=" * 45)
    print(report)
