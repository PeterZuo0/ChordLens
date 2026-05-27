from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.models.common import AnalysisKind, ProjectStatus
from app.models.projects import ProjectSummary
from app.storage.paths import ensure_project_dirs, project_dir


_PROJECTS: dict[str, ProjectSummary] = {}


def list_projects() -> list[ProjectSummary]:
    return list(_PROJECTS.values())


def create_audio_project(title: str, source_file_name: str | None = None) -> ProjectSummary:
    project_id = str(uuid4())
    ensure_project_dirs(project_id)
    project = ProjectSummary(
        id=project_id,
        title=title or "Untitled Song",
        status=ProjectStatus.COMPLETE,
        sourceFileName=source_file_name,
        analysisKind=AnalysisKind.MOCK,
        createdAt=datetime.now(UTC),
    )
    _PROJECTS[project_id] = project
    return project


def get_project(project_id: str) -> ProjectSummary | None:
    return _PROJECTS.get(project_id)


def get_project_dir(project_id: str) -> Path:
    return project_dir(project_id)
