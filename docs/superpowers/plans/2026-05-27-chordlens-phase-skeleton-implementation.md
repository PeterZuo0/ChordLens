# ChordLens Phase Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable local ChordLens skeleton, then add thin end-to-end loops for Audio Studio first and AR Looper second.

**Architecture:** Use a Vite React frontend and FastAPI backend as separate local apps. Keep product modes independent through route-level pages, typed frontend API clients, Pydantic backend contracts, and local filesystem project storage under `data/projects`.

**Tech Stack:** React, Vite, TypeScript, Python, FastAPI, Pydantic, pytest, direct browser Web Audio API for the first AR synth.

---

## Planning Notes

This plan is based on:

- `docs/superpowers/specs/2026-05-27-chordlens-design.md`
- `docs/superpowers/specs/2026-05-27-chordlens-phase-skeleton-design.md`
- `AGENTS.md`

Repository-specific constraints:

- Do not implement code until Peter approves this implementation plan.
- Do not commit until Peter has completed code review and explicitly approves the commit.
- Do not push until Peter explicitly approves the push.
- Do not add Demucs, MediaPipe, Tone.js, SQLite, cloud services, account systems, or YouTube extraction in this plan.
- Treat all audio analysis in Phase 2 as mock or best-effort and label it clearly in API data and UI.

The writing-plans skill normally includes commit steps. This repository's `AGENTS.md` overrides that. Each task ends with a review checkpoint instead of a commit.

## Proposed File Structure

Create:

```text
frontend/
  package.json
  pnpm-lock.yaml
  index.html
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
  src/
    main.tsx
    app/
      App.tsx
      routes.ts
    pages/
      HomePage.tsx
      AudioStudioPage.tsx
      ArLooperPage.tsx
      NotFoundPage.tsx
    api/
      client.ts
      types.ts
    audio-studio/
      AudioUploadPanel.tsx
      AnalysisSummary.tsx
      ChordTimeline.tsx
      StemControls.tsx
    ar-looper/
      ArControls.tsx
      ChordTimeline.tsx
      synth.ts
      types.ts
    styles/
      global.css
backend/
  requirements.txt
  app/
    __init__.py
    main.py
    api/
      __init__.py
      health.py
      projects.py
      audio.py
    core/
      __init__.py
      config.py
    models/
      __init__.py
      common.py
      projects.py
      audio.py
    services/
      __init__.py
      project_store.py
      mock_analysis.py
    storage/
      __init__.py
      paths.py
  tests/
    test_health.py
    test_audio_projects.py
data/
  .gitkeep
  projects/
    .gitkeep
```

Modify:

```text
README.md
.gitignore
```

Only create `.gitignore` if it does not already exist. It should ignore generated dependencies, virtual environments, Python caches, frontend build output, and runtime project data while keeping `data/.gitkeep` and `data/projects/.gitkeep`.

## Phase 1 Tasks: Runnable Skeleton

### Task 1: Add Repository Runtime Boundaries

**Files:**

- Create: `.gitignore`
- Create: `data/.gitkeep`
- Create: `data/projects/.gitkeep`
- Modify: `README.md`

- [ ] **Step 1: Inspect current repository state**

Run:

```powershell
git status --short
rg --files
```

Expected:

- Existing documentation changes remain untouched.
- No frontend or backend implementation exists yet.

- [ ] **Step 2: Add ignore rules**

Create `.gitignore` with rules for:

```gitignore
# Frontend
frontend/node_modules/
frontend/dist/
frontend/.vite/

# Python
backend/.venv/
backend/**/__pycache__/
backend/.pytest_cache/
*.pyc

# Local runtime data
data/projects/*
!data/projects/.gitkeep

# Local env
.env
.env.*
!.env.example
```

- [ ] **Step 3: Add data placeholders**

Create:

```text
data/.gitkeep
data/projects/.gitkeep
```

- [ ] **Step 4: Update README with local app sections**

Add sections for:

- project layout
- Phase 1 startup commands
- Phase 2 direction
- local data warning: do not commit uploaded audio or generated analysis

- [ ] **Step 5: Review checkpoint**

Run:

```powershell
git diff -- README.md .gitignore
git status --short
```

Expected:

- Only intended docs/config/data placeholder files changed.
- No implementation files yet.

### Task 2: Scaffold FastAPI Backend

**Files:**

- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/health.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: Write backend requirements**

Create `backend/requirements.txt`:

```text
fastapi
uvicorn[standard]
python-multipart
pytest
httpx
```

- [ ] **Step 2: Write health test first**

Create `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["app"] == "ChordLens"
```

- [ ] **Step 3: Run test to verify failure before implementation**

Run:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests/test_health.py -v
```

Expected:

- Initial run fails until app files exist, or passes after the implementation files are created in Step 4.
- If dependency install fails because of restricted network access, request approval for the install command before continuing.

- [ ] **Step 4: Implement FastAPI app and health route**

Create `backend/app/core/config.py`:

```python
from pathlib import Path


APP_NAME = "ChordLens"
APP_VERSION = "0.1.0"
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
PROJECTS_DIR = DATA_DIR / "projects"
```

Create `backend/app/api/health.py`:

```python
from fastapi import APIRouter

from app.core.config import APP_NAME, APP_VERSION


router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router


app = FastAPI(title="ChordLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
```

- [ ] **Step 5: Verify backend health test**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_health.py -v
```

Expected:

- `test_health_returns_ok` passes.

- [ ] **Step 6: Review checkpoint**

Run:

```powershell
git diff -- backend
```

Expected:

- Backend contains only health/config skeleton and one passing test.

### Task 3: Add Backend Project And Stub Audio APIs

**Files:**

- Create: `backend/app/api/projects.py`
- Create: `backend/app/api/audio.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/common.py`
- Create: `backend/app/models/projects.py`
- Create: `backend/app/models/audio.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/project_store.py`
- Create: `backend/app/services/mock_analysis.py`
- Create: `backend/app/storage/__init__.py`
- Create: `backend/app/storage/paths.py`
- Create: `backend/tests/test_audio_projects.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write API contract tests first**

Create `backend/tests/test_audio_projects.py` with tests for:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_list_projects_starts_empty_or_stubbed():
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
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_audio_projects.py -v
```

Expected:

- Tests fail because routes/models/services do not exist yet.

- [ ] **Step 3: Implement Pydantic models**

Create explicit models for:

- `ProjectStatus`: `queued`, `analyzing`, `complete`, `failed`
- `AnalysisKind`: `mock`, `best_effort`, `real`
- `ProjectSummary`
- `CreateAudioProjectRequest`
- `ChordEvent`
- `AnalysisSummary`

- [ ] **Step 4: Implement local project store**

Use a simple in-memory index plus filesystem directory creation for Phase 1:

- create UUID project IDs
- create `data/projects/<project-id>/original`
- create `data/projects/<project-id>/analysis`
- create `data/projects/<project-id>/stems`
- create `data/projects/<project-id>/exports`
- return project summaries

Do not add SQLite yet.

- [ ] **Step 5: Implement mock analysis service**

Return deterministic mock analysis:

```json
{
  "analysisKind": "mock",
  "durationSec": null,
  "bpm": 92,
  "key": "G major",
  "stems": ["vocals", "drums", "bass", "other"],
  "chords": [
    { "timeSec": 0, "chord": "G", "confidence": null },
    { "timeSec": 4, "chord": "C", "confidence": null },
    { "timeSec": 8, "chord": "D", "confidence": null },
    { "timeSec": 12, "chord": "G", "confidence": null }
  ]
}
```

- [ ] **Step 6: Implement routes**

Add:

- `GET /api/projects`
- `POST /api/audio/projects`
- `GET /api/audio/projects/{project_id}`
- `GET /api/audio/projects/{project_id}/analysis`

Mount routers in `backend/app/main.py`.

- [ ] **Step 7: Verify backend API tests**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Expected:

- Health tests pass.
- Audio project API tests pass.

- [ ] **Step 8: Review checkpoint**

Run:

```powershell
git diff -- backend data
```

Expected:

- Backend exposes stub APIs.
- Runtime project directories are ignored except `.gitkeep`.

### Task 4: Scaffold Vite React Frontend

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/app/App.tsx`
- Create: `frontend/src/app/routes.ts`
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/pages/AudioStudioPage.tsx`
- Create: `frontend/src/pages/ArLooperPage.tsx`
- Create: `frontend/src/pages/NotFoundPage.tsx`
- Create: `frontend/src/styles/global.css`

- [ ] **Step 1: Create frontend package manifest**

Use `pnpm`.

Package scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  }
}
```

Dependencies:

- `@vitejs/plugin-react`
- `vite`
- `typescript`
- `react`
- `react-dom`
- `vitest`

Do not add UI frameworks yet.

- [ ] **Step 2: Install frontend dependencies**

Run:

```powershell
cd frontend
pnpm install
```

Expected:

- `pnpm-lock.yaml` is created.
- If dependency install fails because of restricted network access, request approval before continuing.

- [ ] **Step 3: Implement app shell routes without adding a router dependency**

Use a tiny local route switch based on `window.location.pathname` in `App.tsx`.

Routes:

- `/`
- `/audio-studio`
- `/ar-looper`
- fallback not found page

Use regular anchor links for navigation.

- [ ] **Step 4: Implement Phase 1 placeholder pages**

Home page:

- project name
- short local-first description
- navigation links to both modes

Audio Studio page:

- upload area placeholder
- project/status placeholder
- analysis summary placeholder
- stem controls placeholder
- chord timeline placeholder

AR Looper page:

- camera placeholder
- beat buttons: `1`, `2`, `4`, `8`
- chord buttons: `C`, `D`, `E`, `F`, `G`, `A`, `B`
- timeline placeholder
- playback controls placeholder

- [ ] **Step 5: Add restrained app styling**

Use plain CSS in `frontend/src/styles/global.css`.

Design constraints:

- no marketing landing page
- app-like navigation
- no one-hue palette dominance
- compact workbench layout
- cards only for individual tool panels
- responsive layout that does not overlap on small screens

- [ ] **Step 6: Verify frontend build**

Run:

```powershell
cd frontend
pnpm build
```

Expected:

- TypeScript build passes.
- Vite build completes.

- [ ] **Step 7: Review checkpoint**

Run:

```powershell
git diff -- frontend
```

Expected:

- Frontend renders three routes without backend dependency.

### Task 5: Connect Frontend To Backend Health And Stub APIs

**Files:**

- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/types.ts`
- Modify: `frontend/src/pages/HomePage.tsx`
- Modify: `frontend/src/pages/AudioStudioPage.tsx`

- [ ] **Step 1: Define frontend API types**

Create TypeScript types matching backend models:

- `ProjectStatus`
- `AnalysisKind`
- `ProjectSummary`
- `AnalysisSummary`
- `ChordEvent`
- `HealthResponse`

- [ ] **Step 2: Implement API client**

In `frontend/src/api/client.ts`:

- base URL defaults to `http://127.0.0.1:8000`
- `getHealth()`
- `listProjects()`
- `createAudioProject(title: string)`
- `getAudioProjectAnalysis(projectId: string)`

- [ ] **Step 3: Show backend health on home page**

Home page should show:

- backend connected
- backend unavailable
- loading

Keep failure copy practical for local development.

- [ ] **Step 4: Show stub projects/analysis on Audio Studio page**

Add a "Create mock project" action for Phase 1.

On click:

- call `POST /api/audio/projects`
- fetch analysis
- render title/status/mock BPM/key/chords

- [ ] **Step 5: Verify backend/frontend integration manually**

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd frontend
pnpm dev
```

Open:

```text
http://127.0.0.1:5173
```

Expected:

- Home page reports backend connected.
- Audio Studio can create and display a mock project.

- [ ] **Step 6: Verify frontend build after API integration**

Run:

```powershell
cd frontend
pnpm build
```

Expected:

- Build passes.

- [ ] **Step 7: Review checkpoint**

Run:

```powershell
git diff -- frontend backend README.md
```

Expected:

- Phase 1 runnable skeleton is complete.

## Phase 2 Tasks: Thin End-to-End MVP, Audio First

### Task 6: Implement Audio File Upload Contract

**Files:**

- Modify: `backend/app/api/audio.py`
- Modify: `backend/app/models/audio.py`
- Modify: `backend/app/services/project_store.py`
- Modify: `backend/tests/test_audio_projects.py`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/audio-studio/AudioUploadPanel.tsx`
- Modify: `frontend/src/pages/AudioStudioPage.tsx`

- [ ] **Step 1: Add failing backend upload tests**

Tests should cover:

- accepts `.mp3`, `.wav`, `.m4a`
- rejects unsupported extension with `400`
- stores source file under `data/projects/<project-id>/original/source.<ext>`
- returns project status and `analysisKind: "mock"`

- [ ] **Step 2: Run backend upload tests to verify failure**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_audio_projects.py -v
```

Expected:

- New upload tests fail before implementation.

- [ ] **Step 3: Implement upload endpoint**

Add:

```text
POST /api/audio/uploads
```

Behavior:

- accepts multipart file upload
- validates extension
- creates project
- stores uploaded file as `original/source.<ext>`
- writes mock analysis artifacts
- returns `ProjectSummary`

- [ ] **Step 4: Write mock analysis artifacts**

Create:

```text
analysis/summary.json
analysis/chords.json
analysis/beats.json
```

Contents can be deterministic mock data. Include `analysisKind: "mock"`.

- [ ] **Step 5: Verify backend upload tests pass**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Expected:

- All backend tests pass.

- [ ] **Step 6: Implement frontend upload client**

Add `uploadAudioFile(file: File)` to `frontend/src/api/client.ts`.

- [ ] **Step 7: Implement AudioUploadPanel**

UI behavior:

- file picker accepts `.mp3,.wav,.m4a`
- upload action
- uploading state
- success state
- unsupported file error
- backend error display

- [ ] **Step 8: Wire upload result into Audio Studio page**

After upload:

- display project summary
- fetch and display analysis
- show mock label clearly

- [ ] **Step 9: Verify frontend build**

Run:

```powershell
cd frontend
pnpm build
```

Expected:

- Build passes.

- [ ] **Step 10: Manual upload verification**

Use a tiny local dummy file with an allowed extension for API contract verification. Do not claim audio decoding or real analysis.

Expected:

- project directory is created
- uploaded file is stored
- mock JSON artifacts are created
- UI displays mock analysis

- [ ] **Step 11: Review checkpoint**

Run:

```powershell
git diff -- backend frontend data
```

Expected:

- Audio Studio thin upload loop is complete.
- Runtime uploaded files remain ignored by Git.

### Task 7: Build Audio Studio Display Components

**Files:**

- Create: `frontend/src/audio-studio/AnalysisSummary.tsx`
- Create: `frontend/src/audio-studio/ChordTimeline.tsx`
- Create: `frontend/src/audio-studio/StemControls.tsx`
- Modify: `frontend/src/pages/AudioStudioPage.tsx`
- Modify: `frontend/src/styles/global.css`

- [ ] **Step 1: Extract analysis summary component**

Show:

- title
- status
- analysis kind
- BPM
- key
- duration if known, otherwise `Unknown`

- [ ] **Step 2: Extract chord timeline component**

Render chord events in time order.

Each item shows:

- time
- chord
- confidence if available, otherwise `mock`

- [ ] **Step 3: Extract stem controls component**

Render stems:

- vocals
- drums
- bass
- other

Controls should be visibly disabled or labeled as placeholder until real stems exist.

- [ ] **Step 4: Keep UI copy honest**

The page must state that Phase 2 uses mock analysis until real pipelines are connected.

- [ ] **Step 5: Verify build**

Run:

```powershell
cd frontend
pnpm build
```

Expected:

- Build passes.

- [ ] **Step 6: Manual browser check**

Open `/audio-studio`.

Expected:

- No layout overlap on desktop.
- Mock status is obvious.
- Upload/result workflow remains usable.

- [ ] **Step 7: Review checkpoint**

Run:

```powershell
git diff -- frontend/src/audio-studio frontend/src/pages/AudioStudioPage.tsx frontend/src/styles/global.css
```

Expected:

- Audio Studio UI is split into focused components.

### Task 8: Build AR Looper Manual Thin Loop

**Files:**

- Create: `frontend/src/ar-looper/types.ts`
- Create: `frontend/src/ar-looper/synth.ts`
- Create: `frontend/src/ar-looper/ArControls.tsx`
- Create: `frontend/src/ar-looper/ChordTimeline.tsx`
- Modify: `frontend/src/pages/ArLooperPage.tsx`
- Modify: `frontend/src/styles/global.css`

- [ ] **Step 1: Define AR loop types**

Types:

```ts
export type BeatLength = 1 | 2 | 4 | 8;
export type ChordName = "C" | "D" | "E" | "F" | "G" | "A" | "B";

export interface ChordLoopEvent {
  id: string;
  chord: ChordName;
  beats: BeatLength;
  createdAt: string;
}
```

- [ ] **Step 2: Implement minimal Web Audio synth**

In `synth.ts`:

- create audio context on user gesture
- map major triads to frequencies
- play a short soft chord preview
- release oscillators cleanly

Do not add Tone.js in this task.

- [ ] **Step 3: Implement manual controls**

UI behavior:

- selected beat length
- selected chord
- commit button
- preview chord on commit
- append event to timeline
- undo
- clear

- [ ] **Step 4: Add camera placeholder**

Show a clearly labeled camera preview placeholder. Do not request camera permission unless specifically included in a later approved task.

- [ ] **Step 5: Add state-machine placeholder note in code**

Add a concise code comment near commit logic:

```ts
// Future hand tracking should feed this same commit boundary after hover stabilization.
```

- [ ] **Step 6: Verify frontend build**

Run:

```powershell
cd frontend
pnpm build
```

Expected:

- Build passes.

- [ ] **Step 7: Manual browser check**

Open `/ar-looper`.

Expected:

- selecting beat/chord works
- commit adds timeline event
- undo and clear work
- chord preview plays after a user gesture
- camera area does not claim real tracking exists

- [ ] **Step 8: Review checkpoint**

Run:

```powershell
git diff -- frontend/src/ar-looper frontend/src/pages/ArLooperPage.tsx frontend/src/styles/global.css
```

Expected:

- AR thin loop is manual, local, and ready for future hand-tracking adapter.

### Task 9: Update Documentation For Running And Verifying

**Files:**

- Modify: `README.md`

- [ ] **Step 1: Document setup**

Add:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```powershell
cd frontend
pnpm install
```

- [ ] **Step 2: Document local run commands**

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
pnpm dev
```

- [ ] **Step 3: Document verification commands**

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Frontend:

```powershell
cd frontend
pnpm build
```

- [ ] **Step 4: Document current limitations**

State:

- Audio analysis is mock/best-effort in this phase.
- Stem separation is not implemented yet.
- AR hand tracking is not implemented yet.
- YouTube extraction is intentionally out of scope.
- Runtime files under `data/projects` should not be committed.

- [ ] **Step 5: Review checkpoint**

Run:

```powershell
git diff -- README.md
```

Expected:

- README matches actual implemented behavior.

### Task 10: Final Verification Before Human Code Review

**Files:**

- No direct edits unless verification finds issues.

- [ ] **Step 1: Run backend tests**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Expected:

- All backend tests pass.

- [ ] **Step 2: Run frontend build**

Run:

```powershell
cd frontend
pnpm build
```

Expected:

- Build passes.

- [ ] **Step 3: Start backend**

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Expected:

- Backend starts on `http://127.0.0.1:8000`.

- [ ] **Step 4: Start frontend**

Run:

```powershell
cd frontend
pnpm dev
```

Expected:

- Frontend starts on `http://127.0.0.1:5173`.

- [ ] **Step 5: Manual app smoke test**

Check:

- `/` loads and shows backend health.
- `/audio-studio` uploads an allowed file and displays mock analysis.
- `/ar-looper` manually creates chord events and plays preview audio.
- unsupported upload extension shows a clear error.
- no UI page implies real Demucs, real MediaPipe, or perfect analysis.

- [ ] **Step 6: Ask Peter about Chrome inspection**

Per `AGENTS.md`, after UI implementation ask whether to connect Chrome for UI/UX and functional inspection.

If Peter agrees:

- inspect running UI in Chrome
- check layout, responsiveness, interactions, visual polish, obvious accessibility issues
- fix issues directly
- re-check affected UI

If Peter declines:

- state that local verification did not include Chrome inspection

- [ ] **Step 7: Prepare review summary**

Summarize:

- files changed
- verification commands run
- known limitations
- whether Chrome inspection was performed
- no commit has been made

## Execution Order

Recommended order:

1. Task 1: repository boundaries
2. Task 2: backend health skeleton
3. Task 3: backend project and stub APIs
4. Task 4: frontend route skeleton
5. Task 5: frontend/backend Phase 1 integration
6. Task 6: Audio Studio upload thin loop
7. Task 7: Audio Studio display components
8. Task 8: AR Looper manual thin loop
9. Task 9: README update
10. Task 10: final verification

Stop after Task 5 if Peter wants Phase 1 reviewed before Phase 2 begins.

## Approval Gate

Do not implement this plan until Peter approves it.

After implementation, do not commit or push until Peter reviews the code and explicitly approves those actions.
