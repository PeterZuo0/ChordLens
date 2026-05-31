import io
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app


def write_fake_wav(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt ")


@pytest.fixture
def isolated_stem_root(monkeypatch, tmp_path):
    import app.services.stem_sessions as stem_sessions

    root = tmp_path / "stem_sessions"
    monkeypatch.setattr(stem_sessions, "STEM_SESSIONS_DIR", root)
    return root


@pytest.fixture
def completed_session(isolated_stem_root):
    import app.services.stem_sessions as stem_sessions

    session_id = "safe_session_123"
    session_dir = isolated_stem_root / session_id
    output_root = session_dir / "demucs-output"
    for stem_name in stem_sessions.DEMUCS_STEM_NAMES:
        write_fake_wav(output_root / "htdemucs" / "sample" / f"{stem_name}.wav")

    items = stem_sessions.normalize_demucs_output(output_root, session_dir, session_id)
    stem_sessions.build_stems_zip(session_id)
    return session_id, items


def test_create_stem_session_normalizes_demucs_output(isolated_stem_root):
    import app.services.stem_sessions as stem_sessions

    session_id = "safe_session_123"
    session_dir = isolated_stem_root / session_id
    output_root = session_dir / "demucs-output"
    for stem_name in stem_sessions.DEMUCS_STEM_NAMES:
        write_fake_wav(output_root / "htdemucs" / "sample" / f"{stem_name}.wav")

    items = stem_sessions.normalize_demucs_output(output_root, session_dir, session_id)

    assert {item.name for item in items} == {"vocals", "drums", "bass", "other"}
    assert all(item.status == "complete" for item in items)
    assert all(item.streamUrl for item in items)
    assert all(item.downloadUrl for item in items)
    assert all(item.fileSizeBytes and item.fileSizeBytes > 0 for item in items)
    for stem_name in stem_sessions.DEMUCS_STEM_NAMES:
        assert (session_dir / "stems" / f"{stem_name}.wav").exists()


def test_rejects_path_traversal_session_ids(isolated_stem_root):
    import app.services.stem_sessions as stem_sessions

    with pytest.raises(HTTPException):
        stem_sessions.resolve_session_dir("../bad")


def test_rejects_invalid_stem_names(isolated_stem_root):
    import app.services.stem_sessions as stem_sessions

    with pytest.raises(HTTPException):
        stem_sessions.resolve_stem_path("safeid", "../source")


def test_zip_download_contains_four_stems(isolated_stem_root, completed_session):
    import app.services.stem_sessions as stem_sessions

    session_id, _ = completed_session
    archive = stem_sessions.build_stems_zip(session_id)

    with zipfile.ZipFile(archive) as zip_file:
        assert sorted(zip_file.namelist()) == ["bass.wav", "drums.wav", "other.wav", "vocals.wav"]


def test_stem_stream_endpoint_serves_existing_stem(isolated_stem_root, completed_session):
    client = TestClient(app)
    session_id, _ = completed_session

    response = client.get(f"/api/audio/stem-sessions/{session_id}/stems/vocals")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")


def test_single_stem_download_uses_safe_filename(isolated_stem_root, completed_session):
    client = TestClient(app)
    session_id, _ = completed_session

    response = client.get(f"/api/audio/stem-sessions/{session_id}/stems/vocals/download")

    assert response.status_code == 200
    assert "vocals.wav" in response.headers["content-disposition"]


def test_zip_endpoint_downloads_all_stems(isolated_stem_root, completed_session):
    client = TestClient(app)
    session_id, _ = completed_session

    response = client.get(f"/api/audio/stem-sessions/{session_id}/download")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/zip")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        assert sorted(zip_file.namelist()) == ["bass.wav", "drums.wav", "other.wav", "vocals.wav"]


def test_clear_session_deletes_files_and_later_returns_404(isolated_stem_root, completed_session):
    client = TestClient(app)
    session_id, _ = completed_session

    delete_response = client.delete(f"/api/audio/stem-sessions/{session_id}")
    stream_response = client.get(f"/api/audio/stem-sessions/{session_id}/stems/vocals")

    assert delete_response.status_code == 204
    assert stream_response.status_code == 404


def test_clear_session_retires_session_even_when_file_cleanup_is_blocked(isolated_stem_root, completed_session, monkeypatch):
    import app.services.stem_sessions as stem_sessions

    session_id, _ = completed_session

    def fail_cleanup(path):
        raise PermissionError("file is busy")

    monkeypatch.setattr(stem_sessions.shutil, "rmtree", fail_cleanup)

    stem_sessions.clear_session(session_id)

    with pytest.raises(HTTPException):
        stem_sessions.resolve_session_dir(session_id)
