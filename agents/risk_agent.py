
"""Interface for the preliminary environmental risk review agent."""

from typing import Any, Dict

from agents.nodes import risk_node
from agents.state import ScreeningState


def run_risk_agent(
    project_details: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the preliminary keyword-based environmental topic review.

    This is not a detailed environmental risk assessment.
    """

    if not isinstance(project_details, dict):
        raise TypeError("project_details must be a dictionary.")

    state: ScreeningState = {
        "project_details": project_details,
        "errors": [],
    }

    result = risk_node(state)

    return result.get("risk_assessment", {})


if __name__ == "__main__":
    sample_project = {
        "project_type": "Industrial project",
        "project_location": "Example industrial area, Karnataka",
        "proposed_activity": "Manufacturing facility",
        "project_capacity": "Not yet specified",
        "water_usage": "Groundwater extraction",
        "waste_generation": "Industrial wastewater",
    }

    risk_result = run_risk_agent(sample_project)

    print("\nPRELIMINARY ENVIRONMENTAL RISK AGENT")
    print("=" * 45)
    print(risk_result)
