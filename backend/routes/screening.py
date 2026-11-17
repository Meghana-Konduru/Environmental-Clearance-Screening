from fastapi import APIRouter, HTTPException

from backend.schemas.project import ProjectDetails
from backend.services.screening_service import perform_screening

router = APIRouter()


@router.post("/screen")
def screen_project(project: ProjectDetails):

    project_data = project.model_dump(exclude_none=True)

    result = perform_screening(project_data)

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )

    return result