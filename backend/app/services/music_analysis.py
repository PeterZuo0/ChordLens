from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np

from app.models.audio import ChordHint, TempoCandidate, TransientMusicAnalysis
from app.services.audio_features import build_onset_envelope, split_harmonic_percussive, trim_for_analysis
from app.services.structure_analysis import analyze_song_structure


PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
MAJOR_PROFILE = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
MINOR_PROFILE = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)


def analyze_music_features(samples: np.ndarray, sample_rate: int) -> TransientMusicAnalysis:
    clean = trim_for_analysis(samples, sample_rate)
    bpm, candidates, bpm_confidence, bpm_message = estimate_bpm_candidates(clean, sample_rate)
    key, key_confidence, alternatives = estimate_key_from_audio(clean, sample_rate)
    result = TransientMusicAnalysis(
        bpm=bpm,
        key=key,
        confidence=key_confidence,
        bpmConfidence=bpm_confidence,
        bpmCandidates=candidates,
        bpmMessage=bpm_message,
        keyConfidence=key_confidence,
        keyAlternatives=alternatives,
        chordHints=build_chord_hints(clean, sample_rate),
        structure=analyze_song_structure(clean, sample_rate),
    )
    return result


def estimate_bpm_candidates(
    samples: np.ndarray,
    sample_rate: int,
) -> tuple[int | None, list[TempoCandidate], float | None, str | None]:
    if samples.size < sample_rate or float(np.max(np.abs(samples), initial=0.0)) < 1e-5:
        return None, [], None, "Insufficient rhythmic energy for BPM estimate."

    harmonic, percussive = split_harmonic_percussive(samples)
    raw: list[tuple[float, float, str]] = []
    for source, source_samples in (("full_onset", samples), ("percussive_onset", percussive), ("harmonic_onset", harmonic)):
        tempo = _librosa_tempo(source_samples, sample_rate)
        if tempo is not None:
            strength = _onset_strength_score(source_samples, sample_rate)
            raw.append((tempo, strength, source))
        peak_tempo = _peak_interval_tempo(source_samples, sample_rate)
        if peak_tempo is not None:
            raw.append((peak_tempo, 0.58, f"{source}_peaks"))

    candidates = _normalize_scored_tempo_candidates(raw)
    if not candidates:
        return None, [], None, "No stable tempo candidate found."
    best = candidates[0]
    return best.bpm, candidates, best.confidence, None


def normalize_tempo_candidates(raw_tempos: Iterable[float]) -> list[TempoCandidate]:
    return _normalize_scored_tempo_candidates([(tempo, 0.5, "manual") for tempo in raw_tempos])


def estimate_key_from_audio(samples: np.ndarray, sample_rate: int) -> tuple[str | None, float | None, list[str]]:
    if samples.size == 0 or float(np.max(np.abs(samples), initial=0.0)) < 1e-5:
        return None, None, []
    harmonic, _ = split_harmonic_percussive(samples)
    chroma = _chroma(harmonic, sample_rate)
    if chroma is None:
        return None, None, []
    values = chroma.mean(axis=1)
    scored = _score_keys(values)
    if not scored:
        return None, None, []
    best_key, best_score = scored[0]
    second_score = scored[1][1] if len(scored) > 1 else best_score
    confidence = max(0.0, min(1.0, float(best_score - second_score)))
    alternatives = [key for key, _ in scored[1:4]]
    return best_key, round(confidence, 4), alternatives


def build_chord_hints(samples: np.ndarray, sample_rate: int) -> list[ChordHint]:
    if samples.size == 0 or sample_rate <= 0 or float(np.max(np.abs(samples), initial=0.0)) < 1e-5:
        return []
    window_sec = 2.0
    window = max(1, int(window_sec * sample_rate))
    hints: list[ChordHint] = []
    for start in range(0, len(samples), window):
        end = min(len(samples), start + window)
        if end - start < sample_rate:
            continue
        chroma = _chroma(samples[start:end], sample_rate)
        if chroma is None:
            continue
        chord, confidence = _estimate_chord(chroma.mean(axis=1))
        if chord and confidence >= 0.42:
            hints.append(
                ChordHint(
                    startSec=round(start / sample_rate, 3),
                    endSec=round(end / sample_rate, 3),
                    chord=chord,
                    confidence=round(confidence, 4),
                    quality="high" if confidence >= 0.7 else "medium",
                )
            )
    return _merge_chord_hints(hints)


def _librosa_tempo(samples: np.ndarray, sample_rate: int) -> float | None:
    try:
        import librosa

        onset = build_onset_envelope(samples, sample_rate)
        if onset.size == 0 or float(np.max(onset, initial=0.0)) <= 1e-6:
            return None
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset, sr=sample_rate)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if tempo.size else 0.0
        tempo = float(tempo)
        return tempo if math.isfinite(tempo) and tempo > 0 else None
    except Exception:
        return None


def _peak_interval_tempo(samples: np.ndarray, sample_rate: int) -> float | None:
    onset = build_onset_envelope(samples, sample_rate)
    if onset.size < 4:
        return None
    threshold = float(np.mean(onset) + np.std(onset) * 0.8)
    peaks = [index for index in range(1, onset.size - 1) if onset[index] > threshold and onset[index] >= onset[index - 1] and onset[index] >= onset[index + 1]]
    if len(peaks) < 3:
        return None
    intervals = np.diff(peaks)
    median_interval = float(np.median(intervals))
    if median_interval <= 0:
        return None
    hop_length = 512
    tempo = 60 * sample_rate / (median_interval * hop_length)
    return tempo if math.isfinite(tempo) and tempo > 0 else None


def _normalize_scored_tempo_candidates(raw: Iterable[tuple[float, float, str]]) -> list[TempoCandidate]:
    buckets: dict[int, tuple[float, float, str]] = {}
    for tempo, score, source in raw:
        for normalized in _tempo_variants(tempo):
            bpm = int(round(normalized))
            existing = buckets.get(bpm)
            next_score = max(0.1, min(1.0, score))
            if existing is None or next_score > existing[1]:
                buckets[bpm] = (float(tempo), next_score, source)
    merged: list[TempoCandidate] = []
    for bpm, (raw_bpm, score, source) in sorted(buckets.items()):
        if any(abs(bpm - candidate.bpm) <= 2 for candidate in merged):
            continue
        agreement_bonus = min(0.25, sum(1 for other in buckets if abs(other - bpm) <= 2) * 0.05)
        merged.append(TempoCandidate(bpm=bpm, confidence=round(min(1.0, score + agreement_bonus), 4), source=source, rawBpm=round(raw_bpm, 4)))
    return sorted(merged, key=lambda candidate: (-candidate.confidence, candidate.bpm))[:5]


def _tempo_variants(tempo: float) -> list[float]:
    variants = [tempo, tempo / 2, tempo * 2]
    normalized = []
    for value in variants:
        while value < 55:
            value *= 2
        while value > 190:
            value /= 2
        if 55 <= value <= 190:
            normalized.append(value)
    return normalized


def _onset_strength_score(samples: np.ndarray, sample_rate: int) -> float:
    onset = build_onset_envelope(samples, sample_rate)
    if onset.size == 0:
        return 0.1
    value = float(np.mean(onset) + np.std(onset))
    return min(0.78, max(0.25, value / 10))


def _chroma(samples: np.ndarray, sample_rate: int):
    try:
        import librosa

        try:
            return librosa.feature.chroma_cqt(y=samples, sr=sample_rate)
        except Exception:
            return librosa.feature.chroma_stft(y=samples, sr=sample_rate)
    except Exception:
        return None


def _score_keys(chroma_vector) -> list[tuple[str, float]]:
    values = [float(value) for value in chroma_vector]
    if len(values) != 12 or not any(value > 0 for value in values):
        return []
    scored = []
    for tonic in range(12):
        for mode, profile in (("major", MAJOR_PROFILE), ("minor", MINOR_PROFILE)):
            rotated = profile[-tonic:] + profile[:-tonic]
            scored.append((f"{PITCH_CLASSES[tonic]} {mode}", _cosine_similarity(values, rotated)))
    return sorted(scored, key=lambda item: item[1], reverse=True)


def _estimate_chord(chroma_vector) -> tuple[str | None, float]:
    values = np.asarray(chroma_vector, dtype=float)
    if values.size != 12 or float(np.max(values, initial=0.0)) <= 1e-8:
        return None, 0.0
    values = values / (np.linalg.norm(values) or 1.0)
    scored = []
    for tonic in range(12):
        for suffix, intervals in (("", (0, 4, 7)), ("m", (0, 3, 7))):
            template = np.zeros(12)
            for interval in intervals:
                template[(tonic + interval) % 12] = 1.0
            template = template / np.linalg.norm(template)
            scored.append((f"{PITCH_CLASSES[tonic]}{suffix}", float(np.dot(values, template))))
    scored.sort(key=lambda item: item[1], reverse=True)
    best = scored[0]
    second = scored[1][1] if len(scored) > 1 else 0.0
    return best[0], max(0.0, min(1.0, best[1] - second + 0.35))


def _merge_chord_hints(hints: list[ChordHint]) -> list[ChordHint]:
    merged: list[ChordHint] = []
    for hint in hints:
        if merged and merged[-1].chord == hint.chord and abs(merged[-1].endSec - hint.startSec) < 0.05:
            previous = merged[-1]
            merged[-1] = ChordHint(
                startSec=previous.startSec,
                endSec=hint.endSec,
                chord=hint.chord,
                confidence=round(max(previous.confidence, hint.confidence), 4),
                quality=previous.quality if previous.confidence >= hint.confidence else hint.quality,
            )
        else:
            merged.append(hint)
    return merged[:80]


def _cosine_similarity(left: list[float], right: tuple[float, ...]) -> float:
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return -math.inf
    return numerator / (left_norm * right_norm)
