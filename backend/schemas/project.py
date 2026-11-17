from pydantic import BaseModel, Field
from typing import Optional


class ProjectDetails(BaseModel):

    project_type: str
    project_location: str
    proposed_activity: str
    project_capacity: str

    land_requirement: Optional[str] = None
    water_usage: Optional[str] = None
    waste_generation: Optional[str] = None
    emissions: Optional[str] = None
    forest_land: Optional[str] = None
    protected_area_proximity: Optional[str] = None