from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.models.audio import AudioFeatureSummary, AudioVisualizationData, StemInsight


@dataclass(frozen=True)
class LoadedAudio:
    samples: np.ndarray
    sample_rate: int
    duration_sec: float


def load_audio_for_analysis(path: Path, mono: bool = True) -> LoadedAudio:
    import librosa

    samples, sample_rate = librosa.load(path, mono=mono, sr=None)
    samples = np.asarray(samples, dtype=np.float32)
    if samples.ndim > 1:
        samples = np.mean(samples, axis=0)
    duration_sec = float(len(samples) / sample_rate) if sample_rate > 0 else 0.0
    return LoadedAudio(samples=samples, sample_rate=int(sample_rate), duration_sec=round(duration_sec, 3))


def trim_for_analysis(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    if samples.size == 0:
        return samples
    try:
        import librosa

        trimmed, _ = librosa.effects.trim(samples, top_db=45)
        if trimmed.size > sample_rate // 4:
            return np.asarray(trimmed, dtype=np.float32)
    except Exception:
        pass
    return samples


def split_harmonic_percussive(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if samples.size == 0 or float(np.max(np.abs(samples), initial=0.0)) <= 1e-8:
        return samples, samples
    try:
        import librosa

        harmonic, percussive = librosa.effects.hpss(samples)
        return np.asarray(harmonic, dtype=np.float32), np.asarray(percussive, dtype=np.float32)
    except Exception:
        return samples, samples


def build_onset_envelope(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    if samples.size == 0 or sample_rate <= 0:
        return np.asarray([], dtype=np.float32)
    try:
        import librosa

        onset = librosa.onset.onset_strength(y=samples, sr=sample_rate)
        return np.asarray(onset, dtype=np.float32)
    except Exception:
        return np.asarray([], dtype=np.float32)


def summarize_audio_features(samples: np.ndarray, sample_rate: int) -> StemInsight:
    clean = np.asarray(samples, dtype=np.float32)
    if clean.size == 0:
        return StemInsight()

    abs_samples = np.abs(clean)
    rms = _finite_float(math.sqrt(float(np.mean(clean * clean)))) if clean.size else 0.0
    peak = _finite_float(float(np.max(abs_samples, initial=0.0)))
    silence_ratio = _clamp(float(np.mean(abs_samples < 0.01))) if clean.size else 1.0
    onset = build_onset_envelope(clean, sample_rate)
    duration_sec = max(0.001, clean.size / sample_rate) if sample_rate > 0 else 0.001
    onset_density = _finite_float(_count_onset_peaks(onset) / duration_sec)
    transient_strength = _finite_float(float(np.mean(onset)) if onset.size else 0.0)

    low_ratio, mid_ratio, high_ratio = _energy_ratios(clean, sample_rate)
    centroid = _feature_mean(lambda librosa: librosa.feature.spectral_centroid(y=clean, sr=sample_rate))
    rolloff = _feature_mean(lambda librosa: librosa.feature.spectral_rolloff(y=clean, sr=sample_rate))
    flatness = _feature_mean(lambda librosa: librosa.feature.spectral_flatness(y=clean))
    zcr = _feature_mean(lambda librosa: librosa.feature.zero_crossing_rate(y=clean))

    return StemInsight(
        features=AudioFeatureSummary(
            rms=rms,
            peak=peak,
            silenceRatio=silence_ratio,
            lowEnergyRatio=low_ratio,
            midEnergyRatio=mid_ratio,
            highEnergyRatio=high_ratio,
            spectralCentroid=centroid,
            spectralRolloff=rolloff,
            spectralFlatness=flatness,
            zeroCrossingRate=zcr,
            onsetDensity=onset_density,
            transientStrength=transient_strength,
        ),
        visualization=AudioVisualizationData(
            waveform=compact_waveform(clean),
            spectrum=compact_spectrum(clean, sample_rate),
        ),
    )


def compact_waveform(samples: np.ndarray, bins: int = 96) -> list[float]:
    if samples.size == 0:
        return []
    bins = max(1, bins)
    edges = np.linspace(0, samples.size, bins + 1, dtype=int)
    values = []
    for start, end in zip(edges, edges[1:]):
        chunk = samples[start:end]
        values.append(_clamp(float(np.max(np.abs(chunk), initial=0.0)) if chunk.size else 0.0))
    return [round(value, 4) for value in values]


def compact_spectrum(samples: np.ndarray, sample_rate: int, bins: int = 64) -> list[float]:
    if samples.size == 0 or sample_rate <= 0:
        return []
    window = samples[: min(samples.size, sample_rate * 12)]
    if window.size == 0:
        return []
    spectrum = np.abs(np.fft.rfft(window))
    if spectrum.size == 0:
        return []
    edges = np.linspace(0, spectrum.size, max(1, bins) + 1, dtype=int)
    values = []
    max_value = float(np.max(spectrum, initial=0.0)) or 1.0
    for start, end in zip(edges, edges[1:]):
        chunk = spectrum[start:end]
        values.append(_clamp(float(np.mean(chunk)) / max_value if chunk.size else 0.0))
    return [round(value, 4) for value in values]


def _energy_ratios(samples: np.ndarray, sample_rate: int) -> tuple[float | None, float | None, float | None]:
    if samples.size == 0 or sample_rate <= 0:
        return None, None, None
    spectrum = np.abs(np.fft.rfft(samples[: min(samples.size, sample_rate * 12)])) ** 2
    freqs = np.fft.rfftfreq(min(samples.size, sample_rate * 12), 1 / sample_rate)
    total = float(np.sum(spectrum))
    if total <= 1e-12:
        return 0.0, 0.0, 0.0
    low = float(np.sum(spectrum[freqs < 250])) / total
    mid = float(np.sum(spectrum[(freqs >= 250) & (freqs < 4000)])) / total
    high = float(np.sum(spectrum[freqs >= 4000])) / total
    return round(_clamp(low), 4), round(_clamp(mid), 4), round(_clamp(high), 4)


def _feature_mean(factory) -> float | None:
    try:
        import librosa

        value = np.asarray(factory(librosa), dtype=float)
        if value.size == 0:
            return None
        return _finite_float(float(np.nanmean(value)))
    except Exception:
        return None


def _count_onset_peaks(onset: np.ndarray) -> int:
    if onset.size < 3:
        return 0
    threshold = float(np.mean(onset) + np.std(onset) * 0.5)
    return sum(1 for index in range(1, onset.size - 1) if onset[index] > threshold and onset[index] >= onset[index - 1] and onset[index] >= onset[index + 1])


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    if not math.isfinite(value):
        return low
    return max(low, min(high, value))


def _finite_float(value: float | None) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(float(value), 4)
