from __future__ import annotations

import io
import math
import wave
from pathlib import Path


def write_silence_wav(path: Path, duration_sec: float = 1.0, sample_rate: int = 22050) -> None:
    _write_samples(path, [0.0] * int(duration_sec * sample_rate), sample_rate)


def write_sine_wav(path: Path, frequency: float = 440.0, duration_sec: float = 1.0, sample_rate: int = 22050) -> None:
    samples = [
        0.45 * math.sin(2 * math.pi * frequency * frame / sample_rate)
        for frame in range(int(duration_sec * sample_rate))
    ]
    _write_samples(path, samples, sample_rate)


def write_click_wav(path: Path, bpm: int = 120, duration_sec: float = 4.0, sample_rate: int = 22050) -> None:
    samples = _click_samples(bpm=bpm, duration_sec=duration_sec, sample_rate=sample_rate)
    _write_samples(path, samples, sample_rate)


def write_chord_bed_wav(
    path: Path,
    frequencies: list[float],
    duration_sec: float = 4.0,
    sample_rate: int = 22050,
) -> None:
    frame_count = int(duration_sec * sample_rate)
    scale = 0.35 / max(1, len(frequencies))
    samples = []
    for frame in range(frame_count):
        value = sum(math.sin(2 * math.pi * frequency * frame / sample_rate) for frequency in frequencies)
        samples.append(scale * value)
    _write_samples(path, samples, sample_rate)


def write_alternating_sections_wav(path: Path, sample_rate: int = 22050) -> None:
    samples: list[float] = []
    section_specs = [
        (220.0, 0.18, 6.0),
        (440.0, 0.42, 6.0),
        (220.0, 0.2, 6.0),
        (660.0, 0.48, 6.0),
        (330.0, 0.16, 6.0),
    ]
    for frequency, amplitude, duration_sec in section_specs:
        for frame in range(int(duration_sec * sample_rate)):
            samples.append(amplitude * math.sin(2 * math.pi * frequency * frame / sample_rate))
    _write_samples(path, samples, sample_rate)


def build_click_wav(bpm: int = 90, duration_sec: float = 4.0, sample_rate: int = 22050) -> bytes:
    buffer = io.BytesIO()
    _write_wave(buffer, _click_samples(bpm=bpm, duration_sec=duration_sec, sample_rate=sample_rate), sample_rate)
    return buffer.getvalue()


def _click_samples(bpm: int, duration_sec: float, sample_rate: int) -> list[float]:
    frame_count = int(duration_sec * sample_rate)
    beat_interval = max(1, int(sample_rate * 60 / bpm))
    click_width = max(1, int(sample_rate * 0.006))
    samples = [0.0] * frame_count
    for start in range(0, frame_count, beat_interval):
        for offset in range(click_width):
            index = start + offset
            if index < frame_count:
                samples[index] = 0.9 * (1 - offset / click_width)
    return samples


def _write_samples(path: Path, samples: list[float], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output:
        _write_wave(output, samples, sample_rate)


def _write_wave(output, samples: list[float], sample_rate: int) -> None:
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for sample in samples:
            value = int(max(-1.0, min(1.0, sample)) * 32767)
            frames.extend(value.to_bytes(2, byteorder="little", signed=True))
        wav_file.writeframes(bytes(frames))
