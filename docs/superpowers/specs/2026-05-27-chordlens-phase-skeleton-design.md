# ChordLens Phase Skeleton Design

Date: 2026-05-27
Status: Draft for Peter review

## Summary

This spec defines the first two implementation phases for ChordLens. The goal is to move from product design into a runnable local application skeleton without overcommitting to heavy audio or AR dependencies too early.

The selected direction is:

1. Phase 1: build a runnable frontend and backend skeleton with clear page, API, and local storage boundaries.
2. Phase 2: build thin end-to-end product loops for both modes, with Audio Analysis Studio prioritized before AR Chord Looper.

This spec does not approve implementation by itself. Code scaffolding should start only after Peter reviews this spec and approves an implementation plan.

## Goals

- Establish a local-first app structure that can run on a developer machine.
- Keep AR Chord Looper and Audio Analysis Studio as independent pages.
- Create clear boundaries for frontend routes, backend APIs, local project storage, and future processing pipelines.
- Make Audio Studio the first meaningful product loop after the skeleton is running.
- Keep Phase 2 thin enough to avoid getting blocked by Demucs, MediaPipe, or chord-recognition model integration.

## Non-Goals

- No cloud deployment.
- No user accounts.
- No YouTube or streaming-platform audio extraction.
- No paid external processing services.
- No full DAW editing surface.
- No production-quality audio analysis claims.
- No TouchDesigner bridge in these phases.

## Phase 1: Runnable Skeleton

Phase 1 creates the application shell and development workflow. It should be useful even before real audio analysis or hand tracking exists.

### Frontend

Use React, Vite, and TypeScript.

Initial routes:

- `/`: lightweight home page with navigation to the two modes.
- `/audio-studio`: Audio Analysis Studio placeholder page.
- `/ar-looper`: AR Chord Looper placeholder page.

The placeholder pages should show the intended major regions of each mode without pretending that real functionality exists.

Audio Studio page regions:

- upload area placeholder
- project/status area placeholder
- analysis summary placeholder
- stem controls placeholder
- chord timeline placeholder

AR Looper page regions:

- camera preview placeholder
- beat selection controls
- chord selection controls
- timeline placeholder
- playback controls placeholder

### Backend

Use Python FastAPI.

Initial API surface:

- `GET /health`: returns backend health and version metadata.
- `GET /api/projects`: returns an empty project list or stub project list.
- `POST /api/audio/projects`: creates a stub audio project record.
- `GET /api/audio/projects/{project_id}`: returns stub project metadata.
- `GET /api/audio/projects/{project_id}/analysis`: returns stub analysis data.

The backend should not run Demucs, librosa, Essentia, or chord models in Phase 1. API responses should make stub/mock status explicit.

### Local Storage Layout

Create or document this local storage shape for future phases:

```text
data/
  projects/
    <project-id>/
      original/
      stems/
      analysis/
      exports/
```

Phase 1 may include `.gitkeep` files or runtime-created directories, but should not require committing user audio files or generated analysis outputs.

### Configuration

Keep configuration local and simple:

- frontend dev server URL
- backend dev server URL
- local data directory
- allowed upload extensions for future use

Use environment files only if needed for local development. Do not introduce deployment or account configuration.

### Verification

Phase 1 is complete when:

- frontend dependencies install successfully
- backend dependencies install successfully
- frontend dev server starts
- backend dev server starts
- `/`, `/audio-studio`, and `/ar-looper` render
- frontend can call `GET /health`
- documented startup commands work on the local machine

## Phase 2: Thin End-to-End MVP, Audio First

Phase 2 turns the skeleton into two thin product loops. Audio Studio gets priority and should be implemented first. AR Looper should still receive a small demonstrable loop so the two-mode product shape remains intact.

## Phase 2A: Audio Studio Thin Loop

Audio Studio should support a local upload-to-result workflow using best-effort or mock analysis.

### User Flow

1. User opens `/audio-studio`.
2. User selects an `mp3`, `wav`, or `m4a` file.
3. Frontend uploads the file to the backend.
4. Backend creates a local project directory.
5. Backend stores the original file under the project.
6. Backend creates an analysis job record.
7. Frontend polls job/project status.
8. Backend returns a completed stub or lightweight analysis result.
9. Frontend displays project metadata, BPM/key placeholders, chord timeline, and stem-control placeholders.

### Backend Behavior

Initial implementation may use synchronous or FastAPI background task processing. It should expose the same status model either way:

- `queued`
- `analyzing`
- `complete`
- `failed`

The first pass can produce deterministic mock analysis JSON, for example:

- duration if cheaply available, otherwise unknown
- BPM placeholder
- key placeholder
- simple chord list
- stem names: `vocals`, `drums`, `bass`, `other`

Any mock or best-effort values must be labeled clearly in API data and UI copy.

### Frontend Behavior

The Audio Studio UI should support:

- file picker
- upload button or automatic upload after selection
- upload/progress/status states
- project summary display
- analysis summary display
- chord timeline display
- disabled or placeholder stem controls if real stems do not exist yet

The page should not imply that vocal removal or real stem separation is complete until those pipelines exist.

### Data Artifacts

Expected project directory after an uploaded file:

```text
data/
  projects/
    <project-id>/
      original/
        source.<ext>
      analysis/
        summary.json
        chords.json
        beats.json
```

`stems/` and `exports/` may exist but can remain empty in the first Phase 2A pass.

## Phase 2B: AR Looper Thin Loop

AR Looper should prove the interaction model without requiring full MediaPipe integration immediately.

### User Flow

1. User opens `/ar-looper`.
2. User grants camera permission if camera preview is implemented in this phase.
3. User selects a beat length and chord through UI controls or a mock hover input.
4. User commits a chord event.
5. Frontend appends the event to a timeline.
6. Frontend plays a synthesized chord preview.
7. User can play, pause, undo, or clear the loop if included in the thin pass.

### Interaction Strategy

The code should leave room for the intended state machine:

```text
idle -> hovering -> armed -> committed -> cooldown
```

Phase 2B may implement this with manual UI interactions or mock hover events first. MediaPipe Hand Landmarker can be added later behind a hand-tracking adapter boundary.

### Audio Strategy

Use a minimal browser synth first. Prefer direct Web Audio API unless Tone.js is deliberately approved in the implementation plan as a runtime dependency.

The first chord vocabulary can be major triads only unless Peter approves minor or seventh variants.

## Architecture

### Frontend Modules

Suggested structure:

```text
frontend/
  src/
    app/
    pages/
      HomePage.tsx
      AudioStudioPage.tsx
      ArLooperPage.tsx
    api/
    audio-studio/
    ar-looper/
    styles/
```

Responsibilities:

- `pages/`: route-level page composition.
- `api/`: backend client functions and response types.
- `audio-studio/`: upload workflow, project status, analysis display components.
- `ar-looper/`: beat/chord selection, timeline, synth playback, future hand-tracking adapter.

### Backend Modules

Suggested structure:

```text
backend/
  app/
    main.py
    api/
    core/
    models/
    services/
      projects.py
      audio_jobs.py
    storage/
```

Responsibilities:

- `main.py`: FastAPI app creation and router mounting.
- `api/`: route handlers.
- `models/`: Pydantic request and response models.
- `services/`: project creation, job state, analysis artifact writing.
- `storage/`: local filesystem path handling.

SQLite can wait until the project/job state needs persistence beyond simple local files. If added, it should be approved in the implementation plan.

## Data Contracts

Use explicit response models from the start so frontend and backend can evolve independently.

Example project summary:

```json
{
  "id": "project-id",
  "title": "Uploaded Song",
  "status": "complete",
  "sourceFileName": "song.wav",
  "analysisKind": "mock",
  "createdAt": "2026-05-27T00:00:00Z"
}
```

Example analysis summary:

```json
{
  "projectId": "project-id",
  "analysisKind": "mock",
  "durationSec": null,
  "bpm": 92,
  "key": "G major",
  "stems": ["vocals", "drums", "bass", "other"],
  "chords": [
    { "timeSec": 0, "chord": "G", "confidence": null },
    { "timeSec": 4, "chord": "C", "confidence": null }
  ]
}
```

## Error Handling

Phase 1 should handle:

- backend unavailable from frontend
- unknown routes
- unexpected API response failures

Phase 2 should handle:

- unsupported file extension
- upload failure
- project creation failure
- missing analysis artifacts
- failed analysis job state
- camera permission denied for AR Looper if camera preview is included

Errors should be displayed as actionable local-development messages, not silent console failures.

## Testing And Verification

### Phase 1

- frontend build or typecheck
- backend import/startup check
- backend health endpoint check
- manual browser check for all three routes

### Phase 2

- upload API test with a small sample file or generated dummy file
- project directory creation verification
- analysis JSON creation verification
- frontend manual check for upload/status/result flow
- AR Looper manual check for chord event creation and synth playback

If browser inspection is needed after UI implementation, ask Peter whether to connect Chrome for UI/UX and functional inspection, as required by `AGENTS.md`.

## Open Decisions Before Implementation Plan

- Exact package manager for frontend: npm, pnpm, or another choice.
- Whether the backend should use `uv`, plain `venv + pip`, or another Python workflow.
- Whether Phase 2A should use only mock analysis or attempt lightweight metadata extraction.
- Whether Tone.js should be added in Phase 2B or initial synth playback should use direct Web Audio API.
- Whether SQLite should be introduced in Phase 2 or deferred until project history needs durable indexing.

## Acceptance Criteria

This phase skeleton is accepted when Peter agrees that:

- Phase 1 should create a runnable local frontend/backend skeleton.
- Phase 2 should create thin end-to-end loops for both product modes.
- Audio Studio should be implemented first in Phase 2.
- Heavy dependencies such as Demucs and MediaPipe can be deferred behind clear interfaces.
- The next step is a detailed implementation plan, not immediate code.
