# ChordLens Technical Design

Date: 2026-05-27
Status: Draft approved for planning

## Summary

ChordLens is a local web-based music creation tool with two independent MVP modes:

1. AR Chord Looper: a camera-driven chord loop tool where the user selects beat length with the left hand and chord with the right hand.
2. Audio Analysis Studio: an uploaded-audio analysis workspace for cover-song practice and lightweight remix preparation.

The first release is a local personal tool. It does not include cloud deployment, user accounts, YouTube downloading, a full DAW, fine-grained MIDI transcription, or TouchDesigner integration.

## Product Shape

The app has two primary pages:

- `/ar-looper`: real-time AR chord loop creation.
- `/audio-studio`: uploaded-song analysis, stem playback, and practice controls.

The modes remain separate in V1 to keep implementation and mental models clear. Data structures should leave room for future project interoperability.

## Mode 1: AR Chord Looper

### Goal

Let a user create a chord loop by using two hands in front of a webcam:

- Left hand chooses the beat length.
- Right hand chooses the chord.
- A chord event is committed only when both selections are stable at the same time.

### UI

- Camera feed as the page background.
- Left-side vertical beat controls: `1`, `2`, `4`, `8` beats.
- Right-side chord grid: `C`, `D`, `E`, `F`, `G`, `A`, `B`.
- Bottom timeline showing events such as `C x2 | G x4 | F x1`.
- Top controls for BPM, play/pause, undo, and clear.
- Visual hover and commit feedback for both hands.

### Interaction Model

The gesture system uses a small state machine instead of triggering on raw hit tests:

`idle -> hovering -> armed -> committed -> cooldown`

A commit happens when:

- Left hand is hovering over a beat button.
- Right hand is hovering over a chord button.
- Both selections remain stable for a threshold, initially around 300 ms.
- The system is not in cooldown.

After commit:

- Play the selected chord immediately for feedback.
- Append `{ chord, beats }` to the loop timeline.
- Enter cooldown, initially around 500 ms, to avoid duplicate events.

### Audio Behavior

- Use a synthesizer sound for V1.
- Each chord is synthesized from multiple oscillators through Web Audio API or Tone.js.
- Prefer a soft `triangle` or `sine`-based timbre with ADSR envelope and mild filtering.
- The loop sequencer schedules chord events according to BPM and event beat length.

### Technical Components

- Camera input: browser `getUserMedia`.
- Hand tracking: MediaPipe Hand Landmarker for up to two hands.
- Hit testing: map index-finger tip landmarks to overlay button bounds.
- State machine: stabilize hover, commit, and cooldown behavior.
- Sequencer: in-memory timeline with JSON serialization.
- Audio engine: synth chord playback and loop scheduling.

## Mode 2: Audio Analysis Studio

### Goal

Let a user upload a song file and produce a practical analysis workspace for cover-song practice and lightweight remixing.

### Input

Supported first-pass formats:

- `mp3`
- `wav`
- `m4a`

The project intentionally does not download or extract audio from YouTube or other streaming platforms in V1.

### Core Workflow

1. User uploads an audio file.
2. Backend creates an analysis job.
3. Backend stores the original audio in a local project directory.
4. Pipeline runs stem separation and musical analysis.
5. Frontend shows progress states: uploading, queued, analyzing, complete, failed.
6. User can play stems, mute vocals, inspect chords, and adjust playback.

### Analysis Features

V1 should include:

- Stem separation into `vocals`, `drums`, `bass`, and `other`.
- Vocal removal by muting or reducing the vocals stem.
- BPM detection.
- Key detection.
- Beat grid estimation.
- Chord progression display.
- Basic stem metadata, such as duration and level.

V1 may label broad stem categories but does not attempt complete instrument recognition for every track.

### Playback And Editing

The player should support:

- Play/pause.
- Seek.
- Waveform display.
- Solo/mute per stem.
- Vocal mute for cover practice.
- Speed adjustment.
- Pitch/key adjustment.
- Chord timeline display synchronized to playback.
- Export of analysis JSON.
- Export of a simple vocal-removed backing track if feasible.

### Technical Components

- Backend API: Python FastAPI.
- Background processing: FastAPI BackgroundTasks for MVP, with a later path to RQ/Celery if needed.
- Storage: local file system under `data/projects`.
- Database: SQLite for local project metadata.
- Stem separation: Demucs.
- Audio analysis: librosa and/or Essentia for BPM, key, beat grid, and features.
- Chord analysis: model-backed or library-backed pipeline, treated as best-effort in MVP.
- Frontend playback: Web Audio API, Tone.js, and/or wavesurfer.js.

## Architecture

### Frontend

Recommended stack:

- React
- Vite
- TypeScript
- MediaPipe Hand Landmarker
- Web Audio API or Tone.js
- wavesurfer.js for Audio Studio waveform playback

The frontend owns:

- Page routing.
- Camera permission flow.
- AR overlay and hit testing UI.
- Local interaction state.
- Playback controls.
- Analysis job status display.

### Backend

Recommended stack:

- Python
- FastAPI
- SQLite
- Local filesystem storage
- Demucs
- librosa / Essentia

The backend owns:

- Audio upload handling.
- Project creation.
- Running analysis jobs.
- Reading and writing analysis artifacts.
- Serving processed stems and metadata to the frontend.

### Data Layout

Suggested local storage shape:

```text
data/
  projects/
    <project-id>/
      original/
        source.ext
      stems/
        vocals.wav
        drums.wav
        bass.wav
        other.wav
      analysis/
        summary.json
        chords.json
        beats.json
      exports/
```

### Example AR Event

```json
{
  "chord": "G",
  "beats": 2,
  "createdAt": "2026-05-27T00:00:00Z"
}
```

### Example Audio Project Summary

```json
{
  "id": "project-id",
  "title": "Uploaded Song",
  "durationSec": 213.5,
  "bpm": 92,
  "key": "G major",
  "stems": ["vocals", "drums", "bass", "other"],
  "status": "complete"
}
```

## MVP Scope

### In Scope

- Local-only web app.
- Two independent pages: AR Looper and Audio Studio.
- Webcam-based two-hand hover detection.
- Synth chord playback.
- Loop timeline creation and playback.
- Upload-based audio analysis.
- Stem separation.
- Vocal mute.
- BPM, key, beat grid, and chord display.
- Playback speed and pitch adjustment.

### Out Of Scope For V1

- YouTube downloading or audio extraction.
- User accounts.
- Cloud deployment.
- Full DAW editing.
- Commercial-quality mastering/export.
- Detailed instrument-by-instrument MIDI transcription.
- Arbitrary instrument replacement.
- TouchDesigner integration.

## Future Phases

### Phase 2 Enhancements

- Better chord recognition and confidence display.
- MIDI transcription for suitable stems.
- Instrument replacement using MIDI plus synth/sampler voices.
- Project save/load UI.
- Export stems, backing tracks, MIDI, and analysis packages.

### Phase 3 Installation / TouchDesigner

- WebSocket or OSC bridge from ChordLens to TouchDesigner.
- AR Looper events streamed to visual systems.
- Audio Studio analysis data used as visual control signals.
- Full-screen performance mode for projected installations.

## Risks And Mitigations

### Hand Tracking Latency

Risk: Webcam inference latency makes the interface feel sluggish.

Mitigation: Keep the overlay lightweight, debounce carefully, and make commit feedback obvious. Start with hover triggering instead of pinch gestures.

### False Gesture Commits

Risk: Small hand movement creates duplicate or unintended chord events.

Mitigation: Require simultaneous stable hover and add cooldown after commit.

### Audio Analysis Accuracy

Risk: Chord, key, and beat detection will not be perfect across all songs.

Mitigation: Treat analysis as editable and confidence-based in later versions. MVP should be useful without claiming perfect transcription.

### Heavy Local Processing

Risk: Demucs and analysis may be slow on CPU-only machines.

Mitigation: Show progress clearly, keep jobs asynchronous, and store intermediate artifacts so users do not rerun expensive steps unnecessarily.

## Open Decisions

- Exact chord vocabulary for AR Looper: major-only first, or include minor/7th variants.
- Whether to use Tone.js or lower-level Web Audio directly.
- Which chord recognition pipeline to adopt for V1.
- Whether pitch/time adjustment should be preview-only in browser or rendered into exported files by backend.
