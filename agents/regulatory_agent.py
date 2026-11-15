
"""Interface for the regulatory information retrieval agent."""

from typing import Any, Dict

from agents.nodes import regulatory_node
from agents.state import ScreeningState


def run_regulatory_agent(
    project_details: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Retrieve relevant regulatory information for a project.

    Withdrawn historical documents are excluded by the existing
    regulatory retrieval logic.
    """

    if not isinstance(project_details, dict):
        raise TypeError("project_details must be a dictionary.")

    state: ScreeningState = {
        "project_details": project_details,
        "errors": [],
    }

    result = regulatory_node(state)

    return {
        "regulatory_context": result.get("regulatory_context", []),
        "errors": result.get("errors", []),
    }


if __name__ == "__main__":
    sample_project = {
        "project_type": "Industrial project",
        "project_location": "Example industrial area, Karnataka",
        "proposed_activity": "Manufacturing facility",
        "project_capacity": "Not yet specified",
    }

    regulatory_result = run_regulatory_agent(sample_project)

    print("\nREGULATORY RETRIEVAL AGENT")
    print("=" * 45)

    print("\nRetrieved documents:")
    for document in regulatory_result["regulatory_context"]:
        print(
            f"\nDocument: {document.get('document_name')}"
            f"\nPage: {document.get('page_number')}"
            f"\nStatus: {document.get('applicability_status')}"
        )

    print("\nErrors:")
    print(regulatory_result["errors"])
