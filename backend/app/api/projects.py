from fastapi import APIRouter

from app.models.projects import ProjectListResponse
from app.services.project_store import list_projects


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def get_projects():
    return ProjectListResponse(projects=list_projects())
