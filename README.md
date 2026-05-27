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
- Local stem separation into vocals, drums, bass, and other.
- Vocal mute for cover practice.
- BPM, key, beat grid, and chord progression analysis.
- Stem solo/mute controls.
- Playback speed and pitch adjustment.
- Export analysis data and simple backing-track outputs where feasible.

## Technical Direction

- Frontend: React, Vite, TypeScript.
- AR: MediaPipe Hand Landmarker.
- Audio playback: Web Audio API, Tone.js, and/or wavesurfer.js.
- Backend: Python FastAPI.
- Analysis: Demucs, librosa, Essentia, and local chord-analysis tooling.
- Storage: local filesystem and SQLite.

See the technical design document:

- [`docs/superpowers/specs/2026-05-27-chordlens-design.md`](docs/superpowers/specs/2026-05-27-chordlens-design.md)

## Status

ChordLens is moving from product and technical design into a local runnable skeleton. Implementation should follow the repository workflow in [`AGENTS.md`](AGENTS.md).

## Project Layout

Planned implementation layout:

- `frontend/`: React, Vite, and TypeScript local web app.
- `backend/`: Python FastAPI local API.
- `data/projects/`: local runtime project storage for uploaded audio, generated analysis, stems, and exports.
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

- Audio Studio analysis is mock/best-effort until real local pipelines are connected.
- Stem separation is not implemented yet.
- AR hand tracking is not implemented yet.
- YouTube extraction remains intentionally out of scope.
