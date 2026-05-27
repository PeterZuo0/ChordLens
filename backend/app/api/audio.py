from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import ALLOWED_AUDIO_EXTENSIONS
from app.models.audio import AnalysisSummary, CreateAudioProjectRequest
from app.models.projects import ProjectSummary
from app.services.mock_analysis import build_mock_analysis, write_mock_analysis
from app.services.project_store import create_audio_project, get_project, get_project_dir


router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/projects", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
def create_project(request: CreateAudioProjectRequest):
    project = create_audio_project(title=request.title)
    write_mock_analysis(project.id, get_project_dir(project.id) / "analysis")
    return project


@router.get("/projects/{project_id}", response_model=ProjectSummary)
def get_audio_project(project_id: str):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects/{project_id}/analysis", response_model=AnalysisSummary)
def get_audio_project_analysis(project_id: str):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return build_mock_analysis(project_id)


@router.post("/uploads", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
async def upload_audio(file: UploadFile = File(...)):
    original_name = file.filename or "source"
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported file extension. Allowed: {allowed}")

    title = Path(original_name).stem or "Uploaded Song"
    project = create_audio_project(title=title, source_file_name=original_name)
    root = get_project_dir(project.id)
    target = root / "original" / f"source{extension}"
    target.write_bytes(await file.read())
    write_mock_analysis(project.id, root / "analysis")
    return project
