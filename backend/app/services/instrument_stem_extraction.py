from __future__ import annotations

from pathlib import Path

import numpy as np

from app.models.audio import TransientStemItem


DERIVED_INSTRUMENT_STEMS = ("piano", "strings")


def derive_piano_strings_from_other(stems_dir: Path, session_id: str) -> list[TransientStemItem]:
    other_path = stems_dir / "other.wav"
    if not other_path.exists():
        return []

    try:
        import librosa
        import soundfile

        samples, sample_rate = librosa.load(other_path, mono=False, sr=None)
        source = _as_channel_first(samples)
        piano, strings = _split_other_into_piano_strings(source, sample_rate)
        return [
            _write_derived_stem(stems_dir, session_id, "piano", piano, sample_rate, soundfile),
            _write_derived_stem(stems_dir, session_id, "strings", strings, sample_rate, soundfile),
        ]
    except Exception:
        return []


def _split_other_into_piano_strings(samples: np.ndarray, sample_rate: int) -> tuple[np.ndarray, np.ndarray]:
    import librosa

    if samples.size == 0 or sample_rate <= 0:
        return samples.copy(), samples.copy()

    mono = np.mean(samples, axis=0)
    mono_stft = librosa.stft(mono, n_fft=2048, hop_length=512)
    mono_mag = np.abs(mono_stft)
    if mono_mag.size == 0:
        return samples.copy(), samples.copy()

    onset_weight = _frame_onset_weight(mono_mag)
    freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=2048)[:, np.newaxis]
    piano_band = _soft_bandpass(freqs, low=70.0, high=5200.0, low_width=90.0, high_width=2600.0)
    strings_band = _soft_bandpass(freqs, low=120.0, high=3600.0, low_width=130.0, high_width=2200.0)

    piano_weight = piano_band * (0.28 + 0.82 * onset_weight[np.newaxis, :])
    strings_weight = strings_band * (0.34 + 0.72 * (1.0 - onset_weight[np.newaxis, :]))
    total = np.maximum(piano_weight + strings_weight, 1e-6)
    piano_mask = piano_weight / total
    strings_mask = strings_weight / total

    piano_channels = []
    strings_channels = []
    for channel in samples:
        stft = librosa.stft(channel, n_fft=2048, hop_length=512)
        piano_channels.append(librosa.istft(stft * piano_mask, length=channel.size))
        strings_channels.append(librosa.istft(stft * strings_mask, length=channel.size))

    return _normalize_like_source(np.asarray(piano_channels, dtype=np.float32), samples), _normalize_like_source(
        np.asarray(strings_channels, dtype=np.float32),
        samples,
    )


def _frame_onset_weight(magnitude: np.ndarray) -> np.ndarray:
    if magnitude.shape[1] == 0:
        return np.asarray([], dtype=np.float32)
    flux = np.maximum(0.0, np.diff(magnitude, axis=1, prepend=magnitude[:, :1]))
    frame_flux = np.mean(flux, axis=0)
    scale = float(np.percentile(frame_flux, 92)) or float(np.max(frame_flux, initial=0.0)) or 1.0
    return np.clip(frame_flux / scale, 0.0, 1.0).astype(np.float32)


def _soft_bandpass(freqs: np.ndarray, low: float, high: float, low_width: float, high_width: float) -> np.ndarray:
    low_edge = 1.0 / (1.0 + np.exp(-(freqs - low) / max(1.0, low_width)))
    high_edge = 1.0 / (1.0 + np.exp((freqs - high) / max(1.0, high_width)))
    return np.clip(low_edge * high_edge, 0.0, 1.0).astype(np.float32)


def _as_channel_first(samples: np.ndarray) -> np.ndarray:
    data = np.asarray(samples, dtype=np.float32)
    if data.ndim == 1:
        return data[np.newaxis, :]
    if data.shape[0] <= data.shape[-1]:
        return data
    return data.T


def _normalize_like_source(derived: np.ndarray, source: np.ndarray) -> np.ndarray:
    source_peak = float(np.max(np.abs(source), initial=0.0))
    derived_peak = float(np.max(np.abs(derived), initial=0.0))
    if source_peak <= 1e-8 or derived_peak <= source_peak:
        return np.clip(derived, -1.0, 1.0).astype(np.float32)
    return np.clip(derived * (source_peak / derived_peak), -1.0, 1.0).astype(np.float32)


def _write_derived_stem(stems_dir: Path, session_id: str, stem_name: str, samples: np.ndarray, sample_rate: int, soundfile) -> TransientStemItem:
    target = stems_dir / f"{stem_name}.wav"
    audio = samples.T if samples.ndim == 2 else samples
    soundfile.write(target, audio, sample_rate, subtype="PCM_16")
    return TransientStemItem(
        name=stem_name,
        status="complete",
        format="wav",
        mimeType="audio/wav",
        fileSizeBytes=target.stat().st_size,
        durationSec=None,
        streamUrl=f"/api/audio/stem-sessions/{session_id}/stems/{stem_name}",
        downloadUrl=f"/api/audio/stem-sessions/{session_id}/stems/{stem_name}/download",
    )
