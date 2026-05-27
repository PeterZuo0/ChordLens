# Audio Studio Transient Analysis Design

Date: 2026-05-27

## Context

ChordLens V1 should stay local-first and avoid project history, account systems, cloud storage, paid external services, and YouTube audio extraction. Audio Studio should become a real one-time analysis surface before deeper AR Looper work.

Peter explicitly does not want SQLite or persistent storage for uploaded audio. Uploaded files may be written to temporary files during a request, but must be deleted after processing.

## Goal

Build a real, transient Audio Studio flow:

1. User uploads one local audio file.
2. Frontend sends the file to the backend.
3. Backend analyzes real metadata, BPM, and musical key.
4. Backend optionally runs stem separation when requested.
5. Backend deletes temporary audio artifacts after processing.
6. Frontend keeps the returned result only in current page state.
7. Refreshing the page loses the result.

## Non-Goals

- No SQLite database.
- No persisted uploaded audio files.
- No project history.
- No account system.
- No cloud storage.
- No YouTube audio downloading or extraction.
- No long-lived stem playback files in this iteration.
- No guarantee that BPM, key, or stems are musically perfect.

## User Flow

Default flow:

1. Open `Audio Studio`.
2. Select or drag in an audio file.
3. Leave `Separate stems` off.
4. Run analysis.
5. See file metadata, BPM, and key.
6. Refreshing or leaving the page clears the result.

Optional stem flow:

1. Select or drag in an audio file.
2. Turn on `Separate stems`.
3. Run analysis.
4. See metadata, BPM, key, and stem separation status.
5. Stem files are cleaned up after analysis, so this iteration returns stem names/status only.

## API

### `POST /api/audio/analyze`

Request:

- Content type: `multipart/form-data`
- Fields:
  - `file`: uploaded audio file
  - `separateStems`: boolean-like string, default `false`

Supported input targets for this iteration:

- `.wav`
- `.mp3`
- `.m4a`

Response:

```json
{
  "analysisKind": "best_effort",
  "temporary": true,
  "source": {
    "fileName": "song.wav",
    "format": "wav",
    "fileSizeBytes": 123456,
    "durationSec": 213.5,
    "sampleRate": 44100,
    "channels": 2
  },
  "music": {
    "bpm": 92,
    "key": "G major",
    "confidence": null
  },
  "stems": {
    "requested": true,
    "status": "complete",
    "items": ["vocals", "drums", "bass", "other"]
  }
}
```

Error response should be explicit and user-actionable for:

- Missing file.
- Unsupported file type.
- Decode failure.
- Analysis failure.
- Stem separation unavailable or failed.

## Backend Design

The backend should treat every upload as request-scoped data:

1. Create a temporary directory.
2. Save the uploaded file inside that temporary directory.
3. Read real metadata.
4. Run BPM and key analysis.
5. If requested, run stem separation inside the same temporary scope.
6. Build the JSON response.
7. Delete the temporary directory before the request completes.

Metadata:

- Use `mutagen` for MP3/M4A metadata where appropriate.
- Use audio decoding/library metadata for WAV and decoded analysis data.

BPM/key:

- Use `librosa` or an equivalent local Python audio analysis library.
- Mark results as `best_effort`.
- Return `null` values when analysis cannot produce a reliable result instead of fabricating certainty.

Stems:

- Use Demucs only when `separateStems=true`.
- Default stem separation is off.
- Do not save stems into `data/projects`.
- Do not expose temporary file paths to the frontend.
- This iteration reports stem status and available stem labels only.

## Frontend Design

Audio Studio should present a focused one-time workflow:

- File picker/drop area.
- `Separate stems` toggle, default off.
- Analyze button.
- Loading state.
- Error state.
- Result state with:
  - File name.
  - Format.
  - Duration.
  - Sample rate.
  - Channels.
  - BPM.
  - Key.
  - Best-effort note.
  - Stem status when requested.
- Clear copy that analysis is temporary and refresh clears results.

The result should stay in React state only. Do not add localStorage, IndexedDB, SQLite, or backend persistence.

## Verification

Backend:

- Unit test successful WAV analysis with a generated small test file.
- Unit test unsupported file type returns a clear error.
- Unit test `separateStems=false` does not call stem separation.
- Unit test temp files are cleaned after request processing where practical.

Frontend:

- Build passes.
- Audio Studio can upload/analyze via mocked or running backend.
- UI shows temporary-state messaging.
- UI handles loading and errors.

Manual:

- Run backend locally.
- Run frontend locally.
- Upload a short test audio file.
- Confirm metadata/BPM/key are returned.
- Confirm result disappears after refresh.

## Acceptance Criteria

- Audio Studio uses the real `/api/audio/analyze` endpoint.
- Uploaded files are not persisted outside request-scoped temporary storage.
- No SQLite or persistent project record is introduced.
- Default analysis returns metadata, BPM, and key.
- Stem separation is controlled by an explicit toggle and is off by default.
- Stem processing, if enabled, is temporary and returns summary/status only.
- Results are clearly described as best-effort and temporary.
- Existing AR Looper functionality remains unaffected.
