from pydantic import BaseModel

from app.models.common import AnalysisKind


class CreateAudioProjectRequest(BaseModel):
    title: str = "Untitled Song"


class ChordEvent(BaseModel):
    timeSec: float
    chord: str
    confidence: float | None = None


class AnalysisSummary(BaseModel):
    projectId: str
    analysisKind: AnalysisKind = AnalysisKind.MOCK
    durationSec: float | None = None
    bpm: int = 92
    key: str = "G major"
    stems: list[str] = ["vocals", "drums", "bass", "other"]
    chords: list[ChordEvent]
