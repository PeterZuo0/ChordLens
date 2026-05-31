from app.services.audio_features import load_audio_for_analysis
from app.services.instrument_analysis import analyze_instruments_for_scope
from audio_fixtures import write_chord_bed_wav, write_click_wav, write_sine_wav


def test_bass_like_audio_scores_electric_bass(tmp_path):
    path = tmp_path / "bass.wav"
    write_sine_wav(path, frequency=82.41, duration_sec=3.0)

    audio = load_audio_for_analysis(path)
    insight = analyze_instruments_for_scope(audio.samples, audio.sample_rate, source="bass")

    assert any(hint.label == "electric_bass" for hint in insight.instrumentHints)


def test_click_like_audio_scores_drum_or_percussion(tmp_path):
    path = tmp_path / "drums.wav"
    write_click_wav(path, bpm=120, duration_sec=4.0)

    audio = load_audio_for_analysis(path)
    insight = analyze_instruments_for_scope(audio.samples, audio.sample_rate, source="drums")
    labels = {hint.label for hint in insight.instrumentHints}

    assert "drum_kit" in labels or "percussion" in labels


def test_instrument_hints_include_evidence_and_visibility(tmp_path):
    path = tmp_path / "pianoish.wav"
    write_chord_bed_wav(path, frequencies=[261.63, 329.63, 392.0], duration_sec=4.0)

    audio = load_audio_for_analysis(path)
    insight = analyze_instruments_for_scope(audio.samples, audio.sample_rate, source="other")

    assert all(hint.evidence for hint in insight.instrumentHints)
    assert all(0 <= hint.confidence <= 1 for hint in insight.instrumentHints)
