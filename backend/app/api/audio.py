from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response

from app.core.config import ALLOWED_AUDIO_EXTENSIONS
from app.models.audio import AnalysisSummary, CreateAudioProjectRequest, TransientAudioAnalysisResponse
from app.models.projects import ProjectSummary
from app.services.mock_analysis import build_mock_analysis, write_mock_analysis
from app.services.project_store import create_audio_project, get_project, get_project_dir
from app.services.stem_sessions import build_stems_zip, clear_session, resolve_stem_path, resolve_zip_path
from app.services.transient_audio_analysis import analyze_upload


router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/analyze", response_model=TransientAudioAnalysisResponse)
async def analyze_audio(file: UploadFile | None = File(None), separateStems: bool = Form(False)):
    if file is None:
        raise HTTPException(status_code=400, detail="Missing audio file.")
    return await analyze_upload(file=file, separate_stems=separateStems)


@router.get("/stem-sessions/{session_id}/stems/{stem_name}")
def stream_stem(session_id: str, stem_name: str):
    stem_path = resolve_stem_path(session_id, stem_name)
    return FileResponse(stem_path, media_type="audio/wav")


@router.get("/stem-sessions/{session_id}/stems/{stem_name}/download")
def download_stem(session_id: str, stem_name: str):
    stem_path = resolve_stem_path(session_id, stem_name)
    return FileResponse(stem_path, media_type="audio/wav", filename=f"{stem_name}.wav")


@router.get("/stem-sessions/{session_id}/download")
def download_stem_zip(session_id: str):
    archive_path = resolve_zip_path(session_id)
    return FileResponse(archive_path, media_type="application/zip", filename="stems.zip")


@router.delete("/stem-sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stem_session(session_id: str):
    clear_session(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
