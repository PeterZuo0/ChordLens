from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.models.common import AnalysisKind, ProjectStatus


class ProjectSummary(BaseModel):
    id: str
    title: str
    status: ProjectStatus
    sourceFileName: str | None = None
    analysisKind: AnalysisKind = AnalysisKind.MOCK
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectListResponse(BaseModel):
    projects: list[ProjectSummary]
