import json
from pathlib import Path

from app.models.audio import AnalysisSummary, ChordEvent
from app.models.common import AnalysisKind


def build_mock_analysis(project_id: str) -> AnalysisSummary:
    return AnalysisSummary(
        projectId=project_id,
        analysisKind=AnalysisKind.MOCK,
        durationSec=None,
        bpm=92,
        key="G major",
        stems=["vocals", "drums", "bass", "other"],
        chords=[
            ChordEvent(timeSec=0, chord="G", confidence=None),
            ChordEvent(timeSec=4, chord="C", confidence=None),
            ChordEvent(timeSec=8, chord="D", confidence=None),
            ChordEvent(timeSec=12, chord="G", confidence=None),
        ],
    )


def write_mock_analysis(project_id: str, analysis_dir: Path) -> AnalysisSummary:
    analysis = build_mock_analysis(project_id)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    summary = analysis.model_dump(mode="json")
    (analysis_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (analysis_dir / "chords.json").write_text(
        json.dumps({"projectId": project_id, "analysisKind": "mock", "chords": summary["chords"]}, indent=2),
        encoding="utf-8",
    )
    (analysis_dir / "beats.json").write_text(
        json.dumps({"projectId": project_id, "analysisKind": "mock", "beats": []}, indent=2),
        encoding="utf-8",
    )
    return analysis
