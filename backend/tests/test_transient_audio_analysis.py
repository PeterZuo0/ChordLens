import io
import subprocess
import wave
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from audio_fixtures import build_click_wav


def build_test_wav(duration_sec: float = 1.0, sample_rate: int = 22050) -> bytes:
    frame_count = int(duration_sec * sample_rate)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


def test_analyze_wav_returns_transient_best_effort_result():
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analysisKind"] == "best_effort"
    assert body["temporary"] is True
    assert body["source"]["fileName"] == "sample.wav"
    assert body["source"]["format"] == "wav"
    assert body["source"]["fileSizeBytes"] > 0
    assert body["source"]["durationSec"] is not None
    assert body["source"]["sampleRate"] == 22050
    assert body["source"]["channels"] == 1
    assert body["music"]["bpm"] is None or body["music"]["bpm"] > 0
    assert body["music"]["key"] is None or isinstance(body["music"]["key"], str)
    assert "bpmConfidence" in body["music"]
    assert "bpmCandidates" in body["music"]
    assert "bpmMessage" in body["music"]
    assert "keyConfidence" in body["music"]
    assert "chordHints" in body["music"]
    assert "structure" in body["music"]
    assert "instrumentSummary" in body["music"]
    assert body["music"]["visualization"]["waveform"]
    assert body["music"]["visualization"]["spectrum"]
    assert body["stems"]["requested"] is False
    assert body["stems"]["status"] == "not_requested"
    assert body["stems"]["items"] == []
    assert body["stems"]["sessionId"] is None
    assert body["stems"]["zipDownloadUrl"] is None


def test_transient_audio_response_serializes_extended_analysis_fields():
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("click.wav", build_click_wav(bpm=90, duration_sec=4.0), "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["music"]["bpmCandidates"], list)
    assert isinstance(body["music"]["structure"], list)
    assert isinstance(body["music"]["instrumentSummary"], list)
    assert isinstance(body["music"]["visualization"]["waveform"], list)


def test_analyze_rejects_unsupported_extension():
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


def test_analyze_rejects_invalid_audio_with_supported_extension():
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("broken.wav", b"not a real wav", "audio/wav")},
    )

    assert response.status_code == 400
    assert "Could not decode audio" in response.json()["detail"]


def test_analyze_without_stems_does_not_invoke_demucs(monkeypatch):
    import app.services.transient_audio_analysis as service

    def fail_if_called(*args, **kwargs):
        raise AssertionError("stem separation should not run")

    monkeypatch.setattr(service, "separate_audio_stems", fail_if_called)
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
        data={"separateStems": "false"},
    )

    assert response.status_code == 200
    assert response.json()["stems"]["status"] == "not_requested"


def test_analyze_reports_demucs_unavailable(monkeypatch):
    import app.services.transient_audio_analysis as service

    real_find_spec = service.importlib.util.find_spec
    monkeypatch.setattr(service.shutil, "which", lambda command: None)
    monkeypatch.setattr(service.importlib.util, "find_spec", lambda name: None if name == "demucs" else real_find_spec(name))
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
        data={"separateStems": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stems"]["requested"] is True
    assert body["stems"]["status"] == "unavailable"
    assert body["stems"]["engine"] == "demucs"
    assert body["stems"]["items"] == []
    assert body["stems"]["zipDownloadUrl"] is None


def test_analyze_uses_python_module_demucs_when_command_is_not_on_path(monkeypatch, tmp_path):
    import app.services.stem_sessions as stem_sessions
    import app.services.transient_audio_analysis as service

    captured_args: list[str] = []
    real_find_spec = service.importlib.util.find_spec
    real_run = service.subprocess.run
    monkeypatch.setattr(service.shutil, "which", lambda command: None)
    monkeypatch.setattr(service.importlib.util, "find_spec", lambda name: object() if name == "demucs" else real_find_spec(name))
    monkeypatch.setattr(stem_sessions, "STEM_SESSIONS_DIR", tmp_path / "stem_sessions")

    def fake_run(args, **kwargs):
        if not isinstance(args, list) or "--out" not in args:
            return real_run(args, **kwargs)
        captured_args.extend(args)
        output_dir = Path(args[args.index("--out") + 1])
        for stem_name in stem_sessions.DEMUCS_STEM_NAMES:
            target = output_dir / "htdemucs" / "sample" / f"{stem_name}.wav"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(build_test_wav(duration_sec=0.1))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(service.subprocess, "run", fake_run)
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
        data={"separateStems": "true"},
    )

    assert response.status_code == 200
    assert captured_args[:3] == [service.sys.executable, "-m", "demucs"]
    assert response.json()["stems"]["status"] == "complete"


def test_analyze_returns_stem_file_metadata_when_demucs_succeeds(monkeypatch, tmp_path):
    import app.services.stem_sessions as stem_sessions
    import app.services.transient_audio_analysis as service

    monkeypatch.setattr(service.shutil, "which", lambda command: "demucs")
    monkeypatch.setattr(stem_sessions, "STEM_SESSIONS_DIR", tmp_path / "stem_sessions")

    def fake_run(args, **kwargs):
        output_dir = Path(args[2])
        for stem_name in stem_sessions.DEMUCS_STEM_NAMES:
            target = output_dir / "htdemucs" / "sample" / f"{stem_name}.wav"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(build_test_wav(duration_sec=0.1))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(service.subprocess, "run", fake_run)
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
        data={"separateStems": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stems"]["requested"] is True
    assert body["stems"]["status"] == "complete"
    assert body["stems"]["engine"] == "demucs+local-dsp"
    assert body["stems"]["sessionId"]
    assert body["stems"]["zipDownloadUrl"]
    assert {item["name"] for item in body["stems"]["items"]} == {"vocals", "drums", "bass", "other", "piano", "strings"}
    assert all(item["streamUrl"] for item in body["stems"]["items"])
    assert all(item["downloadUrl"] for item in body["stems"]["items"])
    assert all(item["fileSizeBytes"] > 0 for item in body["stems"]["items"])


def test_analyze_cleans_temporary_directory(monkeypatch, tmp_path):
    import app.services.transient_audio_analysis as service

    created_roots: list[Path] = []
    real_temporary_directory = service.TemporaryDirectory

    class TrackingTemporaryDirectory:
        def __init__(self, *args, **kwargs):
            self._delegate = real_temporary_directory(dir=tmp_path, *args, **kwargs)

        def __enter__(self):
            value = self._delegate.__enter__()
            created_roots.append(Path(value))
            return value

        def __exit__(self, exc_type, exc, traceback):
            return self._delegate.__exit__(exc_type, exc, traceback)

    monkeypatch.setattr(service, "TemporaryDirectory", TrackingTemporaryDirectory)
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
    )

    assert response.status_code == 200
    assert created_roots
    assert all(not root.exists() for root in created_roots)


def test_analyze_rejects_missing_file_with_clear_error():
    client = TestClient(app)

    response = client.post("/api/audio/analyze")

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing audio file."


def test_analyze_sanitizes_demucs_failure_message(monkeypatch):
    import app.services.transient_audio_analysis as service

    def fake_run(*args, **kwargs):
        temp_path = str(args[0][-1])
        return subprocess.CompletedProcess(args=args[0], returncode=1, stdout="", stderr=f"failed at {temp_path}")

    monkeypatch.setattr(service.shutil, "which", lambda command: "demucs")
    monkeypatch.setattr(service.subprocess, "run", fake_run)
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
        data={"separateStems": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stems"]["status"] == "failed"
    assert "sample.wav" not in body["stems"]["message"]
    assert "source.wav" not in body["stems"]["message"]


def test_analyze_reports_demucs_timeout_as_failed(monkeypatch):
    import app.services.transient_audio_analysis as service

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=900)

    monkeypatch.setattr(service.shutil, "which", lambda command: "demucs")
    monkeypatch.setattr(service.subprocess, "run", fake_run)
    client = TestClient(app)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("sample.wav", build_test_wav(), "audio/wav")},
        data={"separateStems": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stems"]["status"] == "failed"
    assert "timed out" in body["stems"]["message"]
