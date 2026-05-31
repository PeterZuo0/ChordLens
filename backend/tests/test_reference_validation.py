from app.models.audio import (
    InstrumentHint,
    TransientAudioAnalysisResponse,
    TransientAudioSource,
    TransientMusicAnalysis,
    TransientStemAnalysis,
)
from app.services.transient_audio_analysis import analyze_local_audio_file
from audio_fixtures import write_click_wav
from tools.validate_reference_audio import build_reference_summary


def test_reference_summary_reports_missing_expected_instruments():
    response = TransientAudioAnalysisResponse(
        source=TransientAudioSource(fileName="test.wav", format="wav", fileSizeBytes=10),
        music=TransientMusicAnalysis(instrumentSummary=[InstrumentHint(label="strings", confidence=0.7, source="full_mix", evidence=["test"])]),
        stems=TransientStemAnalysis(),
    )

    summary = build_reference_summary(response)

    assert "piano" in summary["missingExpectedInstruments"]
    assert summary["expectedInstrumentCoverage"]["strings"] == "medium"


def test_analyze_local_audio_file_returns_extended_fields(tmp_path):
    path = tmp_path / "click.wav"
    write_click_wav(path, bpm=100, duration_sec=4.0)

    response = analyze_local_audio_file(path, original_name="click.wav", separate_stems=False)

    assert response.music.bpmCandidates or response.music.bpmMessage
    assert isinstance(response.music.structure, list)
    assert isinstance(response.music.instrumentSummary, list)
