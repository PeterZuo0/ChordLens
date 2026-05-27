from fastapi.testclient import TestClient

from app.core.config import PROJECTS_DIR
from app.main import app


def test_list_projects_starts_with_projects_key():
    client = TestClient(app)

    response = client.get("/api/projects")

    assert response.status_code == 200
    assert "projects" in response.json()


def test_create_stub_audio_project():
    client = TestClient(app)

    response = client.post("/api/audio/projects", json={"title": "Test Song"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Test Song"
    assert body["status"] in {"queued", "complete"}
    assert body["analysisKind"] == "mock"


def test_get_stub_analysis_for_project():
    client = TestClient(app)
    project = client.post("/api/audio/projects", json={"title": "Test Song"}).json()

    response = client.get(f"/api/audio/projects/{project['id']}/analysis")

    assert response.status_code == 200
    body = response.json()
    assert body["projectId"] == project["id"]
    assert body["analysisKind"] == "mock"
    assert body["stems"] == ["vocals", "drums", "bass", "other"]


def test_upload_audio_file_creates_project_and_artifacts():
    client = TestClient(app)

    response = client.post(
        "/api/audio/uploads",
        files={"file": ("sample.wav", b"tiny-audio-placeholder", "audio/wav")},
    )

    assert response.status_code == 201
    body = response.json()
    project_dir = PROJECTS_DIR / body["id"]
    assert body["sourceFileName"] == "sample.wav"
    assert body["analysisKind"] == "mock"
    assert (project_dir / "original" / "source.wav").exists()
    assert (project_dir / "analysis" / "summary.json").exists()
    assert (project_dir / "analysis" / "chords.json").exists()
    assert (project_dir / "analysis" / "beats.json").exists()


def test_upload_rejects_unsupported_extension():
    client = TestClient(app)

    response = client.post(
        "/api/audio/uploads",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]
