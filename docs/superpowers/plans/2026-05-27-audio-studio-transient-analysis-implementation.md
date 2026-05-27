# Audio Studio Transient Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Audio Studio mock upload flow with a local, one-time audio analysis flow that returns real metadata, BPM, key, and optional stem status without saving uploads or using SQLite.

**Architecture:** Add a new request-scoped backend analysis service behind `POST /api/audio/analyze`, keeping existing project/mock APIs intact for now. The frontend will call the new endpoint directly and store the result only in React state. Temporary files live inside `tempfile.TemporaryDirectory()` and are deleted before the request returns.

**Tech Stack:** FastAPI, Pydantic, pytest, React, TypeScript, Vite, `mutagen`, `librosa`, optional Demucs subprocess integration.

---

## Constraints

- Follow `AGENTS.md`: do not commit or push without Peter's explicit approval.
- Do not add SQLite, localStorage, IndexedDB, project history, accounts, cloud storage, or YouTube extraction.
- Keep AR Looper untouched except for shared type/CSS changes that are strictly necessary.
- Treat BPM, key, and stems as best-effort.
- Stem separation is off by default and should fail gracefully if Demucs is unavailable.
- Do not expose temporary local file paths to the frontend.

## File Structure

- Modify: `backend/requirements.txt`
  - Add local audio analysis dependencies.
- Modify: `backend/app/models/audio.py`
  - Add request/response models for transient analysis.
- Create: `backend/app/services/transient_audio_analysis.py`
  - Own request-scoped temp-file analysis, metadata extraction, BPM/key estimation, and optional Demucs invocation.
- Modify: `backend/app/api/audio.py`
  - Add `POST /api/audio/analyze`.
  - Keep existing project APIs unchanged.
- Create: `backend/tests/test_transient_audio_analysis.py`
  - Cover generated WAV success, unsupported extension, no stem call by default, temp cleanup, and Demucs-unavailable behavior.
- Modify: `frontend/src/api/types.ts`
  - Add transient analysis response types.
- Modify: `frontend/src/api/client.ts`
  - Add `analyzeAudioFile(file, separateStems)`.
- Modify: `frontend/src/pages/AudioStudioPage.tsx`
  - Replace project/mock UI wiring with transient result state.
- Modify: `frontend/src/audio-studio/AudioUploadPanel.tsx`
  - Add `Separate stems` toggle and "Analyze" action.
- Modify: `frontend/src/audio-studio/AnalysisSummary.tsx`
  - Render transient metadata, BPM, key, best-effort, and temporary-state messaging.
- Modify: `frontend/src/audio-studio/StemControls.tsx`
  - Render requested/not-requested/complete/unavailable/failed summary only.
- Modify: `frontend/src/audio-studio/ChordTimeline.tsx`
  - Either hide from Audio Studio for this iteration or render a neutral no-chords state; do not fabricate chords.
- Modify: `frontend/src/styles/global.css`
  - Small, scoped styles for toggle, status rows, and transient result layout.
- Modify: `README.md`
  - Update Audio Studio startup/behavior notes after implementation.

## Response Contract

Backend model shape:

```python
from typing import Literal

from pydantic import BaseModel, Field


class TransientAudioSource(BaseModel):
    fileName: str
    format: str
    fileSizeBytes: int
    durationSec: float | None = None
    sampleRate: int | None = None
    channels: int | None = None


class TransientMusicAnalysis(BaseModel):
    bpm: int | None = None
    key: str | None = None
    confidence: float | None = None


class TransientStemAnalysis(BaseModel):
    requested: bool = False
    status: Literal["not_requested", "complete", "unavailable", "failed"] = "not_requested"
    items: list[str] = Field(default_factory=list)
    message: str | None = None


class TransientAudioAnalysisResponse(BaseModel):
    analysisKind: AnalysisKind = AnalysisKind.BEST_EFFORT
    temporary: bool = True
    source: TransientAudioSource
    music: TransientMusicAnalysis
    stems: TransientStemAnalysis
```

Frontend type shape should mirror the backend response:

```ts
export interface TransientAudioAnalysisResponse {
  analysisKind: "best_effort";
  temporary: true;
  source: {
    fileName: string;
    format: string;
    fileSizeBytes: number;
    durationSec: number | null;
    sampleRate: number | null;
    channels: number | null;
  };
  music: {
    bpm: number | null;
    key: string | null;
    confidence: number | null;
  };
  stems: {
    requested: boolean;
    status: "not_requested" | "complete" | "unavailable" | "failed";
    items: string[];
    message: string | null;
  };
}
```

## Task 1: Backend Models And Tests

**Files:**
- Modify: `backend/app/models/audio.py`
- Create: `backend/tests/test_transient_audio_analysis.py`

- [ ] **Step 1: Add failing model/API tests**

Create `backend/tests/test_transient_audio_analysis.py` with helper-generated WAV content:

```python
import io
import wave
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


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
    assert body["stems"]["requested"] is False
    assert body["stems"]["status"] == "not_requested"


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
```

- [ ] **Step 2: Run tests to verify failure**

Run from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_transient_audio_analysis.py -v
```

Expected: FAIL because `/api/audio/analyze` and response models do not exist.

- [ ] **Step 3: Add Pydantic models**

In `backend/app/models/audio.py`, add the response models from "Response Contract". Import `Literal` from `typing`.

- [ ] **Step 4: Run targeted tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_transient_audio_analysis.py -v
```

Expected: still FAIL until service and route are implemented.

## Task 2: Request-Scoped Backend Analysis Service

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/services/transient_audio_analysis.py`
- Modify: `backend/tests/test_transient_audio_analysis.py`

- [ ] **Step 1: Add dependencies**

Update `backend/requirements.txt`:

```text
fastapi
uvicorn[standard]
python-multipart
pytest
httpx
mutagen
librosa
soundfile
```

Do not add Demucs to the default requirements in this step. Use subprocess detection so base setup remains lighter; document optional Demucs install separately.

- [ ] **Step 2: Add service skeleton**

Create `backend/app/services/transient_audio_analysis.py`:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException, UploadFile

from app.core.config import ALLOWED_AUDIO_EXTENSIONS
from app.models.audio import (
    TransientAudioAnalysisResponse,
    TransientAudioSource,
    TransientMusicAnalysis,
    TransientStemAnalysis,
)
from app.models.common import AnalysisKind


async def analyze_upload(file: UploadFile, separate_stems: bool = False) -> TransientAudioAnalysisResponse:
    original_name = file.filename or "source"
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported file extension. Allowed: {allowed}")

    with TemporaryDirectory(prefix="chordlens-audio-") as temp_root:
        temp_path = Path(temp_root) / f"source{extension}"
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        temp_path.write_bytes(contents)

        source = inspect_source(temp_path, original_name, len(contents))
        music = analyze_music(temp_path)
        stems = separate_audio_stems(temp_path, temp_root) if separate_stems else TransientStemAnalysis()

        return TransientAudioAnalysisResponse(
            analysisKind=AnalysisKind.BEST_EFFORT,
            temporary=True,
            source=source,
            music=music,
            stems=stems,
        )
```

- [ ] **Step 3: Implement metadata extraction**

In the same file, implement:

```python
def inspect_source(path: Path, original_name: str, size_bytes: int) -> TransientAudioSource:
    # Use mutagen first for container metadata, then librosa/soundfile fallback.
```

Implementation notes:

- Use `mutagen.File(path)` to get duration when available.
- Use `soundfile.info(path)` to get `samplerate`, `channels`, and duration for WAV/decodable files.
- Catch decode/library exceptions and return `None` fields where necessary.
- Do not raise for partial metadata gaps.
- Let the music-analysis stage raise a clear 400 error if the supported file extension cannot be decoded at all.

- [ ] **Step 4: Implement BPM/key analysis**

Add:

```python
def analyze_music(path: Path) -> TransientMusicAnalysis:
    # librosa.load(..., mono=True, sr=None)
    # librosa.beat.beat_track(...)
    # chroma_cqt or chroma_stft for key estimate
```

Decode rule:

- If `librosa.load` cannot decode the file at all, raise `HTTPException(status_code=400, detail="Could not decode audio. Try a valid wav, mp3, or m4a file.")`.
- If decoding succeeds but BPM/key feature extraction is weak or impossible, return `TransientMusicAnalysis(bpm=None, key=None, confidence=None)`.

Key estimation should be a simple local heuristic:

- Compute chroma features.
- Average chroma bins.
- Compare major/minor pitch-class profiles.
- Return strings like `"C major"` or `"A minor"`.
- If decoding succeeds but feature extraction fails or is too weak, return `TransientMusicAnalysis(bpm=None, key=None, confidence=None)`.

- [ ] **Step 5: Implement optional stem subprocess wrapper**

Add:

```python
def separate_audio_stems(path: Path, temp_root: str) -> TransientStemAnalysis:
    # Check shutil.which("demucs") first.
    # If unavailable, return requested=True, status="unavailable", items=[], message="Demucs is not installed."
    # If available, run demucs with output inside temp_root.
```

Implementation notes:

- Use `subprocess.run([...], capture_output=True, text=True, timeout=900, check=False)`.
- Use `--two-stems=vocals` only if the implementation chooses a lighter first pass, otherwise default four stems.
- Return `["vocals", "drums", "bass", "other"]` only after output exists or Demucs exits successfully.
- Do not return file paths.

- [ ] **Step 6: Add service tests for temp cleanup and no stem call**

Append tests:

```python
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

    monkeypatch.setattr(service.shutil, "which", lambda command: None)
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
```

- [ ] **Step 7: Run targeted backend tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_transient_audio_analysis.py -v
```

Expected: still FAIL until route is added.

## Task 3: Backend Route

**Files:**
- Modify: `backend/app/api/audio.py`
- Test: `backend/tests/test_transient_audio_analysis.py`

- [ ] **Step 1: Add route**

In `backend/app/api/audio.py`, import `Form`, the new model, and the service:

```python
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.audio import AnalysisSummary, CreateAudioProjectRequest, TransientAudioAnalysisResponse
from app.services.transient_audio_analysis import analyze_upload
```

Add:

```python
@router.post("/analyze", response_model=TransientAudioAnalysisResponse)
async def analyze_audio(file: UploadFile = File(...), separateStems: bool = Form(False)):
    return await analyze_upload(file=file, separate_stems=separateStems)
```

- [ ] **Step 2: Run targeted backend tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_transient_audio_analysis.py -v
```

Expected: PASS.

- [ ] **Step 3: Run full backend suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Expected: PASS. Existing mock/project tests should continue passing.

## Task 4: Frontend API Types And Client

**Files:**
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/api/client.ts`

- [ ] **Step 1: Add frontend types**

Add the `TransientAudioAnalysisResponse` interface from "Response Contract" to `frontend/src/api/types.ts`.

- [ ] **Step 2: Add client function**

In `frontend/src/api/client.ts`, update imports and add:

```ts
export function analyzeAudioFile(file: File, separateStems: boolean) {
  const body = new FormData();
  body.append("file", file);
  body.append("separateStems", String(separateStems));
  return request<TransientAudioAnalysisResponse>("/api/audio/analyze", {
    method: "POST",
    body
  });
}
```

- [ ] **Step 3: Run frontend build**

Run:

```powershell
npm.cmd run build
```

from `frontend`.

Expected: may fail until UI imports are updated.

## Task 5: Frontend Audio Studio Flow

**Files:**
- Modify: `frontend/src/pages/AudioStudioPage.tsx`
- Modify: `frontend/src/audio-studio/AudioUploadPanel.tsx`
- Modify: `frontend/src/audio-studio/AnalysisSummary.tsx`
- Modify: `frontend/src/audio-studio/StemControls.tsx`
- Modify: `frontend/src/audio-studio/ChordTimeline.tsx`
- Modify: `frontend/src/styles/global.css`

- [ ] **Step 1: Rewire page state**

In `AudioStudioPage.tsx`:

- Remove project creation/import wiring from the active Audio Studio flow.
- Keep `useState<TransientAudioAnalysisResponse | null>`.
- Add `handleAnalyze(file, separateStems)` that calls `analyzeAudioFile`.
- Pass result to summary/stems components.

Target shape:

```tsx
const [analysis, setAnalysis] = useState<TransientAudioAnalysisResponse | null>(null);

async function handleAnalyze(file: File, separateStems: boolean) {
  const nextAnalysis = await analyzeAudioFile(file, separateStems);
  setAnalysis(nextAnalysis);
}
```

- [ ] **Step 2: Update upload panel**

Change props:

```ts
interface AudioUploadPanelProps {
  onAnalyze: (file: File, separateStems: boolean) => Promise<void>;
}
```

Add local state:

```ts
const [separateStems, setSeparateStems] = useState(false);
```

Render:

- File input.
- Checkbox/toggle labeled `Separate stems`.
- Helper copy that stems are slower and temporary.
- Primary button text `Analyze`.

Remove `Create mock project` from the active UI.

- [ ] **Step 3: Update summary component**

Change props to:

```ts
interface AnalysisSummaryProps {
  analysis: TransientAudioAnalysisResponse | null;
}
```

Render:

- Empty state: "Upload a local audio file to run one-time analysis."
- File name, format, size, duration, sample rate, channels.
- BPM and key with `Unknown` fallback.
- `best_effort` label.
- Temporary result message.

- [ ] **Step 4: Update stems component**

Change props:

```ts
interface StemControlsProps {
  stems: TransientAudioAnalysisResponse["stems"] | null;
}
```

Render:

- `not_requested`: "Stem separation was not requested."
- `unavailable`: show message from backend.
- `failed`: show backend message.
- `complete`: list item names without playback buttons.

- [ ] **Step 5: Remove fabricated chord timeline from active page**

For this iteration, do not fabricate chords. In `AudioStudioPage.tsx`, either remove `ChordTimeline` from the rendered layout or pass an empty list with copy explaining chord detection is not part of this increment.

- [ ] **Step 6: Add scoped CSS**

In `frontend/src/styles/global.css`, add only small utility styles:

```css
.toggle-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 14px;
}

.status-note {
  margin-top: 12px;
  border: 1px solid rgba(47, 109, 85, 0.2);
  border-radius: 8px;
  padding: 10px 12px;
  background: #eef7f1;
  color: #355446;
}
```

- [ ] **Step 7: Run frontend build**

Run from `frontend`:

```powershell
npm.cmd run build
```

Expected: PASS.

## Task 6: Documentation And End-To-End Verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README**

Update Audio Studio notes:

- It now uses `POST /api/audio/analyze`.
- Results are temporary and page-local.
- Uploaded files are not persisted.
- BPM/key are best-effort.
- Stem separation requires Demucs installed on PATH and is off by default.

- [ ] **Step 2: Install/update backend dependencies if needed**

Run from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Expected: dependencies installed. If network is blocked, request escalation with approval.

- [ ] **Step 3: Run full backend tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Expected: PASS.

- [ ] **Step 4: Run frontend build**

Run from `frontend`:

```powershell
npm.cmd run build
```

Expected: PASS.

- [ ] **Step 5: Manual local smoke**

Start backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Start frontend:

```powershell
npm.cmd run dev
```

Open `http://127.0.0.1:5173/audio-studio`.

Check:

- Upload generated/short WAV.
- See metadata, BPM/key result or Unknown fallbacks.
- Toggle off by default.
- Refresh clears result.
- With `Separate stems` on and Demucs unavailable, UI shows unavailable status without crashing.

- [ ] **Step 6: UI inspection checkpoint**

Ask Peter whether to connect Chrome for UI/UX and functional inspection. If approved, inspect:

- Default Audio Studio empty state.
- Loading and error states.
- Result layout on desktop and mobile widths.
- Stem unavailable/complete summary states.
- Refresh clears the result.

## Final Review Checklist

- [ ] No SQLite or persistent upload storage added.
- [ ] No `data/projects` writes from `/api/audio/analyze`.
- [ ] No localStorage/IndexedDB added.
- [ ] Mock project APIs still pass existing tests.
- [ ] Audio Studio default flow uses transient endpoint.
- [ ] Results are clearly temporary and best-effort.
- [ ] Stem separation is opt-in.
- [ ] Full backend tests pass.
- [ ] Frontend build passes.
- [ ] Manual browser smoke completed or limitation stated.

## Commit Guidance

Do not commit automatically. After implementation and Peter's code review approval, use one focused commit such as:

```powershell
git add backend frontend README.md docs/superpowers/specs/2026-05-27-audio-studio-transient-analysis-design.md docs/superpowers/plans/2026-05-27-audio-studio-transient-analysis-implementation.md
git commit -m "feat: add transient audio studio analysis"
```
