from __future__ import annotations

import importlib.util
import math
import shutil
import subprocess
import sys
import wave
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
from app.services.audio_features import load_audio_for_analysis, summarize_audio_features
from app.services.instrument_stem_extraction import derive_piano_strings_from_other
from app.services.instrument_analysis import analyze_instruments_for_scope, summarize_full_mix_instruments
from app.services.music_analysis import analyze_music_features
from app.services import stem_sessions


PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
MAJOR_PROFILE = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
MINOR_PROFILE = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)


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

        return analyze_local_audio_file(
            path=temp_path,
            original_name=original_name,
            size_bytes=len(contents),
            separate_stems=separate_stems,
        )


def analyze_local_audio_file(
    path: Path,
    original_name: str | None = None,
    size_bytes: int | None = None,
    separate_stems: bool = False,
) -> TransientAudioAnalysisResponse:
    display_name = original_name or path.name
    source = inspect_source(path, display_name, size_bytes if size_bytes is not None else path.stat().st_size)
    music = analyze_music(path)
    stems = separate_audio_stems(path, str(path.parent)) if separate_stems else TransientStemAnalysis()
    attach_stem_analysis(stems)

    return TransientAudioAnalysisResponse(
        analysisKind=AnalysisKind.BEST_EFFORT,
        temporary=True,
        source=source,
        music=music,
        stems=stems,
    )


def inspect_source(path: Path, original_name: str, size_bytes: int) -> TransientAudioSource:
    duration_sec: float | None = None
    sample_rate: int | None = None
    channels: int | None = None

    try:
        from mutagen import File as MutagenFile

        metadata = MutagenFile(path)
        if metadata is not None and metadata.info is not None:
            duration_sec = _finite_float(getattr(metadata.info, "length", None))
            sample_rate = _positive_int(getattr(metadata.info, "sample_rate", None))
            channels = _positive_int(getattr(metadata.info, "channels", None))
    except Exception:
        pass

    try:
        import soundfile

        info = soundfile.info(path)
        duration_sec = duration_sec if duration_sec is not None else _duration_from_frames(info.frames, info.samplerate)
        sample_rate = sample_rate if sample_rate is not None else _positive_int(info.samplerate)
        channels = channels if channels is not None else _positive_int(info.channels)
    except Exception:
        pass

    if path.suffix.lower() == ".wav" and (duration_sec is None or sample_rate is None or channels is None):
        wav_duration, wav_sample_rate, wav_channels = _inspect_wav(path)
        duration_sec = duration_sec if duration_sec is not None else wav_duration
        sample_rate = sample_rate if sample_rate is not None else wav_sample_rate
        channels = channels if channels is not None else wav_channels

    return TransientAudioSource(
        fileName=original_name,
        format=path.suffix.lower().lstrip("."),
        fileSizeBytes=size_bytes,
        durationSec=duration_sec,
        sampleRate=sample_rate,
        channels=channels,
    )


def analyze_music(path: Path) -> TransientMusicAnalysis:
    try:
        audio = load_audio_for_analysis(path)
    except Exception as issue:
        raise HTTPException(
            status_code=400,
            detail="Could not decode audio. Try a valid wav, mp3, or m4a file.",
        ) from issue

    try:
        music = analyze_music_features(audio.samples, audio.sample_rate)
        music.visualization = summarize_audio_features(audio.samples, audio.sample_rate).visualization
        music.instrumentSummary = summarize_full_mix_instruments(audio.samples, audio.sample_rate)
        return music
    except Exception:
        return TransientMusicAnalysis(bpmMessage="Audio decoded, but detailed music analysis failed.")


def attach_stem_analysis(stems: TransientStemAnalysis) -> None:
    if stems.status != "complete" or not stems.sessionId:
        return
    for item in stems.items:
        try:
            stem_path = stem_sessions.resolve_stem_path(stems.sessionId, item.name)
            audio = load_audio_for_analysis(stem_path)
            item.analysis = analyze_instruments_for_scope(audio.samples, audio.sample_rate, source=item.name)
            item.durationSec = item.durationSec if item.durationSec is not None else audio.duration_sec
        except Exception:
            item.analysis = None


def estimate_key(chroma_vector) -> tuple[str | None, float | None]:
    values = [float(value) for value in chroma_vector]
    if len(values) != 12 or not any(value > 0 for value in values):
        return None, None

    best_score = -math.inf
    second_score = -math.inf
    best_key: str | None = None
    for tonic in range(12):
        for mode, profile in (("major", MAJOR_PROFILE), ("minor", MINOR_PROFILE)):
            rotated = profile[-tonic:] + profile[:-tonic]
            score = _cosine_similarity(values, rotated)
            if score > best_score:
                second_score = best_score
                best_score = score
                best_key = f"{PITCH_CLASSES[tonic]} {mode}"
            elif score > second_score:
                second_score = score

    if best_key is None or not math.isfinite(best_score):
        return None, None

    confidence = max(0.0, min(1.0, best_score - second_score))
    return best_key, confidence


def separate_audio_stems(path: Path, temp_root: str) -> TransientStemAnalysis:
    demucs_command = _demucs_command()
    if demucs_command is None:
        return TransientStemAnalysis(
            requested=True,
            status="unavailable",
            engine="demucs",
            message="Demucs is not installed. Install Demucs and make sure it is available on PATH.",
        )

    session_id, session_dir = stem_sessions.create_session_dir()
    output_dir = session_dir / "demucs-output"
    try:
        result = subprocess.run(
            [*demucs_command, "--out", str(output_dir), str(path)],
            capture_output=True,
            check=False,
            text=True,
            timeout=900,
        )
    except subprocess.TimeoutExpired:
        stem_sessions.clear_session(session_id)
        return TransientStemAnalysis(
            requested=True,
            status="failed",
            engine="demucs",
            message="Demucs stem separation timed out.",
        )
    if result.returncode != 0:
        stem_sessions.clear_session(session_id)
        message = _safe_demucs_error(result.stderr or result.stdout)
        return TransientStemAnalysis(requested=True, status="failed", engine="demucs", message=message)

    try:
        items = stem_sessions.normalize_demucs_output(output_dir, session_dir, session_id)
        derived_items = derive_piano_strings_from_other(session_dir / "stems", session_id)
        items.extend(derived_items)
        stem_sessions.build_stems_zip(session_id)
    except HTTPException:
        stem_sessions.clear_session(session_id)
        return TransientStemAnalysis(
            requested=True,
            status="failed",
            engine="demucs",
            message="Demucs stem separation finished but did not produce the expected local stems.",
        )

    return TransientStemAnalysis(
        requested=True,
        status="complete",
        sessionId=session_id,
        engine="demucs+local-dsp" if derived_items else "demucs",
        items=items,
        zipDownloadUrl=f"/api/audio/stem-sessions/{session_id}/download",
    )


def _demucs_command() -> list[str] | None:
    demucs_path = shutil.which("demucs")
    if demucs_path is not None:
        return [demucs_path]
    if importlib.util.find_spec("demucs") is not None:
        return [sys.executable, "-m", "demucs"]
    return None


def _inspect_wav(path: Path) -> tuple[float | None, int | None, int | None]:
    try:
        with wave.open(str(path), "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            frame_count = wav_file.getnframes()
    except (wave.Error, OSError):
        return None, None, None

    return _duration_from_frames(frame_count, sample_rate), _positive_int(sample_rate), _positive_int(channels)


def _can_decode_wav(path: Path) -> bool:
    duration_sec, sample_rate, channels = _inspect_wav(path)
    return duration_sec is not None and sample_rate is not None and channels is not None


def _duration_from_frames(frame_count: int | None, sample_rate: int | None) -> float | None:
    if frame_count is None or sample_rate is None or sample_rate <= 0:
        return None
    return round(frame_count / sample_rate, 3)


def _positive_int(value) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _finite_float(value) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return round(parsed, 3)


def _cosine_similarity(left: list[float], right: tuple[float, ...]) -> float:
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return -math.inf
    return numerator / (left_norm * right_norm)


def _safe_demucs_error(output: str | None) -> str:
    if not output or not output.strip():
        return "Demucs stem separation failed."
    first_line = output.strip().splitlines()[0]
    if "\\" in first_line or "/" in first_line:
        return "Demucs stem separation failed. Check that the file is supported and Demucs can run locally."
    return first_line[:240]
