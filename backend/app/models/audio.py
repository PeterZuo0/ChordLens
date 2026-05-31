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


class TempoCandidate(BaseModel):
    bpm: int
    confidence: float
    source: str
    rawBpm: float | None = None


class ChordHint(BaseModel):
    startSec: float
    endSec: float
    chord: str
    confidence: float
    quality: Literal["high", "medium", "low"] = "medium"


class StructureSection(BaseModel):
    startSec: float
    endSec: float
    label: Literal["intro", "verse", "pre_chorus", "chorus", "bridge", "interlude", "outro", "unknown"]
    confidence: float
    reason: str | None = None


class InstrumentHint(BaseModel):
    label: Literal[
        "piano",
        "strings",
        "cello_low_strings",
        "violin_high_strings",
        "electric_bass",
        "drum_kit",
        "percussion",
        "synth",
        "acoustic_guitar",
        "vocal",
    ]
    confidence: float
    source: str
    evidence: list[str] = Field(default_factory=list)
    visible: bool = True


class AudioFeatureSummary(BaseModel):
    rms: float | None = None
    peak: float | None = None
    silenceRatio: float | None = None
    lowEnergyRatio: float | None = None
    midEnergyRatio: float | None = None
    highEnergyRatio: float | None = None
    spectralCentroid: float | None = None
    spectralRolloff: float | None = None
    spectralFlatness: float | None = None
    zeroCrossingRate: float | None = None
    onsetDensity: float | None = None
    transientStrength: float | None = None


class AudioVisualizationData(BaseModel):
    waveform: list[float] = Field(default_factory=list)
    spectrum: list[float] = Field(default_factory=list)


class StemInsight(BaseModel):
    features: AudioFeatureSummary = Field(default_factory=AudioFeatureSummary)
    visualization: AudioVisualizationData = Field(default_factory=AudioVisualizationData)
    instrumentHints: list[InstrumentHint] = Field(default_factory=list)


class TransientMusicAnalysis(BaseModel):
    bpm: int | None = None
    key: str | None = None
    confidence: float | None = None
    bpmConfidence: float | None = None
    bpmCandidates: list[TempoCandidate] = Field(default_factory=list)
    bpmMessage: str | None = None
    keyConfidence: float | None = None
    keyAlternatives: list[str] = Field(default_factory=list)
    chordHints: list[ChordHint] = Field(default_factory=list)
    structure: list[StructureSection] = Field(default_factory=list)
    instrumentSummary: list[InstrumentHint] = Field(default_factory=list)
    visualization: AudioVisualizationData = Field(default_factory=AudioVisualizationData)


StemName = Literal["vocals", "drums", "bass", "other", "piano", "strings"]
StemStatus = Literal["queued", "processing", "complete", "unavailable", "failed", "missing"]


class TransientStemItem(BaseModel):
    name: StemName
    status: StemStatus = "complete"
    format: str | None = None
    mimeType: str | None = None
    fileSizeBytes: int | None = None
    durationSec: float | None = None
    streamUrl: str | None = None
    downloadUrl: str | None = None
    message: str | None = None
    analysis: StemInsight | None = None


class TransientStemAnalysis(BaseModel):
    requested: bool = False
    status: Literal["not_requested", "complete", "unavailable", "failed"] = "not_requested"
    sessionId: str | None = None
    engine: str | None = None
    items: list[TransientStemItem] = Field(default_factory=list)
    zipDownloadUrl: str | None = None
    message: str | None = None


class TransientAudioAnalysisResponse(BaseModel):
    analysisKind: AnalysisKind = AnalysisKind.BEST_EFFORT
    temporary: bool = True
    source: TransientAudioSource
    music: TransientMusicAnalysis
    stems: TransientStemAnalysis
