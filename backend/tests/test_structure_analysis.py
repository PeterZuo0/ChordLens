from app.services.audio_features import load_audio_for_analysis
from app.services.structure_analysis import analyze_song_structure
from audio_fixtures import write_alternating_sections_wav, write_sine_wav


def test_structure_sections_are_ordered_and_non_overlapping(tmp_path):
    path = tmp_path / "abab.wav"
    write_alternating_sections_wav(path)

    audio = load_audio_for_analysis(path)
    sections = analyze_song_structure(audio.samples, audio.sample_rate)

    assert len(sections) >= 3
    assert all(section.startSec < section.endSec for section in sections)
    assert all(left.endSec <= right.startSec for left, right in zip(sections, sections[1:]))


def test_short_audio_returns_single_unknown_section(tmp_path):
    path = tmp_path / "short.wav"
    write_sine_wav(path, duration_sec=1.0)

    audio = load_audio_for_analysis(path)
    sections = analyze_song_structure(audio.samples, audio.sample_rate)

    assert len(sections) == 1
    assert sections[0].label == "unknown"
