
"""
LangGraph workflow for the Environmental Clearance
Pre-Screening Service.
"""

from langgraph.graph import StateGraph, START, END

from agents.state import ScreeningState
from agents.nodes import (
    screening_node,
    regulatory_node,
    risk_node,
    report_node,
)


def create_screening_graph():
    """
    Create and compile the environmental clearance
    pre-screening workflow.
    """

    workflow = StateGraph(ScreeningState)

    # Register workflow nodes.
    workflow.add_node("screening", screening_node)
    workflow.add_node("regulatory", regulatory_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("report", report_node)

    # Define execution order.
    workflow.add_edge(START, "screening")
    workflow.add_edge("screening", "regulatory")
    workflow.add_edge("regulatory", "risk")
    workflow.add_edge("risk", "report")
    workflow.add_edge("report", END)

    # Compile the workflow.
    return workflow.compile()


def run_screening(project_details: dict):
    """
    Execute the complete screening workflow.

    Args:
        project_details: Project information supplied by the user.

    Returns:
        Final LangGraph state containing all agent outputs.
    """

    if not isinstance(project_details, dict):
        raise ValueError("Project details must be provided as a dictionary.")

    initial_state = {
        "project_details": project_details,
        "screening_result": {},
        "regulatory_context": [],
        "risk_assessment": {},
        "final_report": {},
        "current_step": "started",
        "errors": [],
    }

    graph = create_screening_graph()

    return graph.invoke(initial_state)


if __name__ == "__main__":

    sample_project = {
        "project_type": "Industrial project",
        "project_location": "Example industrial area, Karnataka",
        "proposed_activity": "Manufacturing facility",
        "project_capacity": "Not yet specified",
    }

    print("\nENVIRONMENTAL CLEARANCE SCREENING")
    print("=" * 60)

    result = run_screening(sample_project)

    print("\nWorkflow status:", result.get("current_step"))

    print("\nScreening observations:")
    print(result.get("screening_result"))

    print("\nRetrieved regulatory documents:")
    for document in result.get("regulatory_context", []):
        print(
            document.get("document_name"),
            "| Page:",
            document.get("page_number"),
        )

    print("\nRisk assessment:")
    print(result.get("risk_assessment"))

    print("\nFinal report:")
    print(result.get("final_report"))

    print("\nErrors:")
    print(result.get("errors"))
