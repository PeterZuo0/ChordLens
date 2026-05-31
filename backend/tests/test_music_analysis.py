from app.services.audio_features import load_audio_for_analysis
from app.services.music_analysis import analyze_music_features, normalize_tempo_candidates
from audio_fixtures import write_chord_bed_wav, write_click_wav, write_silence_wav


def test_estimate_bpm_returns_candidate_for_click_track(tmp_path):
    path = tmp_path / "click90.wav"
    write_click_wav(path, bpm=90, duration_sec=12.0)

    audio = load_audio_for_analysis(path)
    result = analyze_music_features(audio.samples, audio.sample_rate)

    assert result.bpm is not None
    assert abs(result.bpm - 90) <= 3
    assert result.bpmCandidates
    assert result.bpmConfidence is not None


def test_estimate_bpm_reports_degraded_message_for_silence(tmp_path):
    path = tmp_path / "silence.wav"
    write_silence_wav(path, duration_sec=4.0)

    audio = load_audio_for_analysis(path)
    result = analyze_music_features(audio.samples, audio.sample_rate)

    assert result.bpm is None
    assert result.bpmCandidates == []
    assert result.bpmMessage


def test_bpm_candidate_normalization_keeps_pop_ballad_range():
    candidates = normalize_tempo_candidates([38.0, 76.0, 152.0])

    assert any(candidate.bpm == 76 for candidate in candidates)


def test_key_estimation_returns_confidence_for_c_major_chord_bed(tmp_path):
    path = tmp_path / "c_major.wav"
    write_chord_bed_wav(path, frequencies=[261.63, 329.63, 392.0], duration_sec=4.0)

    audio = load_audio_for_analysis(path)
    result = analyze_music_features(audio.samples, audio.sample_rate)

    assert result.key is not None
    assert result.keyConfidence is not None
    assert 0 <= result.keyConfidence <= 1


def test_chord_hints_detect_simple_c_major_bed(tmp_path):
    path = tmp_path / "c_major.wav"
    write_chord_bed_wav(path, frequencies=[261.63, 329.63, 392.0], duration_sec=6.0)

    audio = load_audio_for_analysis(path)
    result = analyze_music_features(audio.samples, audio.sample_rate)

    assert any(hint.chord.startswith("C") for hint in result.chordHints)


def test_chord_hints_suppress_silence(tmp_path):
    path = tmp_path / "silence.wav"
    write_silence_wav(path, duration_sec=4.0)

    audio = load_audio_for_analysis(path)
    result = analyze_music_features(audio.samples, audio.sample_rate)

    assert result.chordHints == []
