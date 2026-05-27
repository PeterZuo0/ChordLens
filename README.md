# ChordLens

ChordLens is a local web-based music creation tool for AR chord looping, audio stem separation, chord analysis, and cover-song practice.

## Vision

ChordLens combines two music creation workflows:

- **AR Chord Looper**: use a webcam and two-hand hover gestures to choose beat length and chords, then build a loop with immediate synth playback.
- **Audio Analysis Studio**: upload an audio file, separate stems, remove vocals, detect BPM/key/chords, and adjust speed or pitch for cover practice and lightweight remixing.

The first version is designed as a local personal tool. It intentionally avoids YouTube audio extraction, cloud deployment, user accounts, and full DAW complexity.

## Planned MVP

### AR Chord Looper

- Webcam-based hand tracking.
- Left hand selects beat length.
- Right hand selects chord.
- Simultaneous hover commits a chord event.
- Synth chord preview and loop timeline playback.
- BPM, play/pause, undo, and clear controls.

### Audio Analysis Studio

- Upload `mp3`, `wav`, or `m4a` files.
- One-time local metadata, BPM, and key analysis.
- Optional local stem separation summary when Demucs is installed.
- Results stay in the current page state and are cleared on refresh.
- Uploaded files are processed in temporary storage and are not persisted.
- Later iterations may add chord progression analysis, stem playback, vocal mute, speed, and pitch tools.
- Playback speed and pitch adjustment.
- Export analysis data and simple backing-track outputs where feasible.

## Technical Direction

- Frontend: React, Vite, TypeScript.
- AR: MediaPipe Hand Landmarker.
- Audio playback: Web Audio API, Tone.js, and/or wavesurfer.js.
- Backend: Python FastAPI.
- Analysis: mutagen, librosa, optional Demucs, and later local chord-analysis tooling.
- Storage: local filesystem for planned project data; transient Audio Studio uploads are not saved.

See the technical design document:

- [`docs/superpowers/specs/2026-05-27-chordlens-design.md`](docs/superpowers/specs/2026-05-27-chordlens-design.md)

## Status

ChordLens is moving from product and technical design into a local runnable skeleton. Implementation should follow the repository workflow in [`AGENTS.md`](AGENTS.md).

## Project Layout

Planned implementation layout:

- `frontend/`: React, Vite, and TypeScript local web app.
- `backend/`: Python FastAPI local API.
- `data/projects/`: local runtime project storage for project-based features. The transient Audio Studio endpoint does not write here.
- `docs/superpowers/specs/`: product and technical specs.
- `docs/superpowers/plans/`: implementation plans.

Runtime files under `data/projects` are local working data and should not be committed.

## Local Development

Backend setup:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Backend run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend setup:

```powershell
cd frontend
npm.cmd install
```

Frontend run:

```powershell
cd frontend
npm.cmd run dev
```

## Verification

Backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

Frontend build:

```powershell
cd frontend
npm.cmd run build
```

## Current Phase Notes

- Audio Studio uses `POST /api/audio/analyze` for one-time best-effort analysis.
- Audio Studio does not use SQLite and does not persist uploaded files.
- BPM and key are best-effort. If local analysis dependencies are unavailable or the file is weak for analysis, values may be `Unknown`.
- Stem separation is optional, off by default, and requires Demucs on `PATH`. This iteration returns stem status only, not playable stem files.
- AR hand tracking is not implemented yet.
- YouTube extraction remains intentionally out of scope.
