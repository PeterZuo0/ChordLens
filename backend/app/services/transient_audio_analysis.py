from __future__ import annotations

import math
import shutil
import subprocess
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
        import librosa
    except Exception:
        if path.suffix.lower() == ".wav" and _can_decode_wav(path):
            return TransientMusicAnalysis()
        raise HTTPException(
            status_code=400,
            detail="Could not decode audio. Try a valid wav, mp3, or m4a file.",
        )

    try:
        samples, sample_rate = librosa.load(path, mono=True, sr=None)
    except Exception as issue:
        raise HTTPException(
            status_code=400,
            detail="Could not decode audio. Try a valid wav, mp3, or m4a file.",
        ) from issue

    try:
        tempo, _ = librosa.beat.beat_track(y=samples, sr=sample_rate)
        bpm = _positive_int(round(float(tempo)))
    except Exception:
        bpm = None

    try:
        chroma = librosa.feature.chroma_stft(y=samples, sr=sample_rate)
        key, confidence = estimate_key(chroma.mean(axis=1))
    except Exception:
        key = None
        confidence = None

    return TransientMusicAnalysis(bpm=bpm, key=key, confidence=confidence)


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
    demucs_path = shutil.which("demucs")
    if demucs_path is None:
        return TransientStemAnalysis(
            requested=True,
            status="unavailable",
            message="Demucs is not installed. Install Demucs and make sure it is available on PATH.",
        )

    output_dir = Path(temp_root) / "stems"
    try:
        result = subprocess.run(
            [demucs_path, "--out", str(output_dir), str(path)],
            capture_output=True,
            check=False,
            text=True,
            timeout=900,
        )
    except subprocess.TimeoutExpired:
        return TransientStemAnalysis(
            requested=True,
            status="failed",
            message="Demucs stem separation timed out.",
        )
    if result.returncode != 0:
        message = _safe_demucs_error(result.stderr or result.stdout)
        return TransientStemAnalysis(requested=True, status="failed", message=message)

    return TransientStemAnalysis(
        requested=True,
        status="complete",
        items=["vocals", "drums", "bass", "other"],
    )


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
