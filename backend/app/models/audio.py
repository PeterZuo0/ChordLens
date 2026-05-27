from typing import Literal

from pydantic import BaseModel, Field

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
    stems: list[str] = Field(default_factory=lambda: ["vocals", "drums", "bass", "other"])
    chords: list[ChordEvent]


class TransientAudioSource(BaseModel):
    fileName: str
    format: str
    fileSizeBytes: int
    durationSec: float | None = None
    sampleRate: int | None = None
    channels: int | None = None


class TransientMusicAnalysis(BaseModel):
    bpm: int | None = None
    key: str | None = None
    confidence: float | None = None


class TransientStemAnalysis(BaseModel):
    requested: bool = False
    status: Literal["not_requested", "complete", "unavailable", "failed"] = "not_requested"
    items: list[str] = Field(default_factory=list)
    message: str | None = None


class TransientAudioAnalysisResponse(BaseModel):
    analysisKind: AnalysisKind = AnalysisKind.BEST_EFFORT
    temporary: bool = True
    source: TransientAudioSource
    music: TransientMusicAnalysis
    stems: TransientStemAnalysis
