import pytest

from app.services.audio_features import load_audio_for_analysis, summarize_audio_features
from audio_fixtures import write_click_wav, write_silence_wav, write_sine_wav


def test_decode_audio_returns_mono_samples_and_rate(tmp_path):
    path = tmp_path / "tone.wav"
    write_sine_wav(path, frequency=440, duration_sec=1.0)

    audio = load_audio_for_analysis(path)

    assert audio.sample_rate > 0
    assert audio.samples.ndim == 1
    assert audio.duration_sec == pytest.approx(1.0, abs=0.05)


def test_feature_summary_has_bounded_visual_arrays(tmp_path):
    path = tmp_path / "click.wav"
    write_click_wav(path, bpm=120, duration_sec=4.0)

    audio = load_audio_for_analysis(path)
    summary = summarize_audio_features(audio.samples, audio.sample_rate)

    assert summary.features.silenceRatio is not None
    assert 0 <= summary.features.silenceRatio <= 1
    assert len(summary.visualization.waveform) <= 128
    assert len(summary.visualization.spectrum) <= 96


def test_hpss_and_onset_envelope_are_safe_for_silence(tmp_path):
    path = tmp_path / "silence.wav"
    write_silence_wav(path, duration_sec=1.0)

    audio = load_audio_for_analysis(path)
    features = summarize_audio_features(audio.samples, audio.sample_rate)

    assert features.features.rms is not None
    assert features.features.onsetDensity is not None
