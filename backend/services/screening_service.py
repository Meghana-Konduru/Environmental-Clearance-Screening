from agents.graph import run_screening


def perform_screening(project_details: dict):

    try:
        result = run_screening(project_details)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }