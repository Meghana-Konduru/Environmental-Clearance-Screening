
"""Interface for the preliminary project screening agent."""

from typing import Any, Dict

from agents.nodes import screening_node
from agents.state import ScreeningState


def run_screening_agent(
    project_details: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the preliminary screening node independently.

    This checks the availability of basic project information.
    It does not make a statutory environmental clearance decision.
    """

    if not isinstance(project_details, dict):
        raise TypeError("project_details must be a dictionary.")

    state: ScreeningState = {
        "project_details": project_details,
        "errors": [],
    }

    result = screening_node(state)

    return result.get("screening_result", {})


if __name__ == "__main__":
    sample_project = {
        "project_type": "Industrial project",
        "project_location": "Example industrial area, Karnataka",
        "proposed_activity": "Manufacturing facility",
        "project_capacity": "Not yet specified",
    }

    screening_result = run_screening_agent(sample_project)

    print("\nPRELIMINARY SCREENING AGENT")
    print("=" * 45)
    print(screening_result)
