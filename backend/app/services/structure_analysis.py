from __future__ import annotations

import math

import numpy as np

from app.models.audio import StructureSection
from app.services.audio_features import build_onset_envelope


def analyze_song_structure(
    samples: np.ndarray,
    sample_rate: int,
    duration_sec: float | None = None,
) -> list[StructureSection]:
    duration = duration_sec if duration_sec is not None else _duration(samples, sample_rate)
    if duration <= 0:
        return []
    if duration < 8:
        return [StructureSection(startSec=0.0, endSec=round(duration, 3), label="unknown", confidence=0.35, reason="too_short")]

    features = extract_section_feature_frames(samples, sample_rate)
    boundaries = detect_boundaries(features, duration)
    sections = _sections_from_boundaries(boundaries)
    return label_sections(sections, features)


def extract_section_feature_frames(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    duration = _duration(samples, sample_rate)
    if duration <= 0:
        return np.zeros((0, 4), dtype=float)
    window_sec = 8.0 if duration >= 80 else 6.0
    hop = max(1, int(window_sec * sample_rate))
    rows = []
    onset = build_onset_envelope(samples, sample_rate)
    onset_per_second = len(onset) / max(duration, 0.001)
    for start in range(0, len(samples), hop):
        chunk = samples[start : start + hop]
        if chunk.size == 0:
            continue
        rms = float(np.sqrt(np.mean(chunk * chunk))) if chunk.size else 0.0
        centroid = _spectral_centroid(chunk, sample_rate)
        zcr = float(np.mean(np.abs(np.diff(np.signbit(chunk))))) if chunk.size > 1 else 0.0
        energy = float(np.mean(np.abs(chunk)))
        rows.append([rms, centroid / 5000, zcr, energy + onset_per_second * 0.001])
    return np.asarray(rows, dtype=float)


def detect_boundaries(feature_frames: np.ndarray, duration_sec: float) -> list[float]:
    if duration_sec <= 0:
        return [0.0]
    frame_count = len(feature_frames)
    if frame_count <= 1:
        return [0.0, round(duration_sec, 3)]

    section_count = max(3, min(10, int(round(duration_sec / 35)) + 3))
    section_count = min(section_count, frame_count)
    boundaries = [0.0]

    if frame_count > 2:
        deltas = np.linalg.norm(np.diff(feature_frames, axis=0), axis=1)
        candidate_indexes = np.argsort(deltas)[::-1][: max(0, section_count - 1)]
        for index in sorted(int(candidate) + 1 for candidate in candidate_indexes):
            time_sec = duration_sec * index / frame_count
            if 6 <= time_sec <= duration_sec - 6:
                boundaries.append(round(time_sec, 3))

    if len(boundaries) < section_count:
        for index in range(1, section_count):
            boundaries.append(round(duration_sec * index / section_count, 3))

    boundaries.append(round(duration_sec, 3))
    return _merge_close_boundaries(sorted(set(boundaries)), min_gap=6.0)


def label_sections(sections: list[tuple[float, float]], feature_frames: np.ndarray) -> list[StructureSection]:
    if not sections:
        return []
    energies = feature_frames[:, 0] if feature_frames.size else np.asarray([0.0])
    median_energy = float(np.median(energies)) if energies.size else 0.0
    result: list[StructureSection] = []
    last_index = len(sections) - 1
    for index, (start, end) in enumerate(sections):
        if len(sections) == 1:
            label = "unknown"
            reason = "single_section"
            confidence = 0.35
        elif index == 0:
            label = "intro"
            reason = "first_section"
            confidence = 0.58
        elif index == last_index:
            label = "outro"
            reason = "last_section"
            confidence = 0.58
        elif index == last_index - 1 and len(sections) >= 5:
            label = "bridge"
            reason = "late_contrast_section"
            confidence = 0.46
        else:
            frame_index = min(len(energies) - 1, max(0, int(index * len(energies) / len(sections))))
            energy = float(energies[frame_index]) if energies.size else 0.0
            if energy >= median_energy:
                label = "chorus"
                reason = "higher_energy_section"
                confidence = 0.52
            elif index % 3 == 2:
                label = "interlude"
                reason = "lower_energy_middle_section"
                confidence = 0.42
            else:
                label = "verse"
                reason = "lower_energy_section"
                confidence = 0.5
        result.append(
            StructureSection(
                startSec=round(start, 3),
                endSec=round(end, 3),
                label=label,
                confidence=confidence,
                reason=reason,
            )
        )
    return result


def _sections_from_boundaries(boundaries: list[float]) -> list[tuple[float, float]]:
    return [(left, right) for left, right in zip(boundaries, boundaries[1:]) if right > left]


def _merge_close_boundaries(boundaries: list[float], min_gap: float) -> list[float]:
    if not boundaries:
        return []
    merged = [boundaries[0]]
    for boundary in boundaries[1:-1]:
        if boundary - merged[-1] >= min_gap:
            merged.append(boundary)
    if boundaries[-1] - merged[-1] < min_gap and len(merged) > 1:
        merged.pop()
    merged.append(boundaries[-1])
    return merged


def _duration(samples: np.ndarray, sample_rate: int) -> float:
    return float(len(samples) / sample_rate) if sample_rate > 0 else 0.0


def _spectral_centroid(samples: np.ndarray, sample_rate: int) -> float:
    if samples.size == 0 or sample_rate <= 0:
        return 0.0
    spectrum = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1 / sample_rate)
    total = float(np.sum(spectrum))
    if total <= 1e-12 or not math.isfinite(total):
        return 0.0
    return float(np.sum(freqs * spectrum) / total)
