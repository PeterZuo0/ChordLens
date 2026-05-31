export type ProjectStatus = "queued" | "analyzing" | "complete" | "failed";
export type AnalysisKind = "mock" | "best_effort" | "real";

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
}

export interface ProjectSummary {
  id: string;
  title: string;
  status: ProjectStatus;
  sourceFileName: string | null;
  analysisKind: AnalysisKind;
  createdAt: string;
}

export interface ProjectListResponse {
  projects: ProjectSummary[];
}

export interface ChordEvent {
  timeSec: number;
  chord: string;
  confidence: number | null;
}

export interface AnalysisSummary {
  projectId: string;
  analysisKind: AnalysisKind;
  durationSec: number | null;
  bpm: number;
  key: string;
  stems: string[];
  chords: ChordEvent[];
}

export interface TransientAudioAnalysisResponse {
  analysisKind: "best_effort";
  temporary: true;
  source: {
    fileName: string;
    format: string;
    fileSizeBytes: number;
    durationSec: number | null;
    sampleRate: number | null;
    channels: number | null;
  };
  music: {
    bpm: number | null;
    key: string | null;
    confidence: number | null;
    bpmConfidence: number | null;
    bpmCandidates: TempoCandidate[];
    bpmMessage: string | null;
    keyConfidence: number | null;
    keyAlternatives: string[];
    chordHints: ChordHint[];
    structure: StructureSection[];
    instrumentSummary: InstrumentHint[];
    visualization: AudioVisualizationData;
  };
  stems: {
    requested: boolean;
    status: "not_requested" | "complete" | "unavailable" | "failed";
    sessionId: string | null;
    engine: string | null;
    items: TransientStemItem[];
    zipDownloadUrl: string | null;
    message: string | null;
  };
}

export type StemName = "vocals" | "drums" | "bass" | "other" | "piano" | "strings";
export type StemStatus = "queued" | "processing" | "complete" | "unavailable" | "failed" | "missing";

export interface TransientStemItem {
  name: StemName;
  status: StemStatus;
  format: string | null;
  mimeType: string | null;
  fileSizeBytes: number | null;
  durationSec: number | null;
  streamUrl: string | null;
  downloadUrl: string | null;
  message: string | null;
  analysis: StemInsight | null;
}

export interface TempoCandidate {
  bpm: number;
  confidence: number;
  source: string;
  rawBpm: number | null;
}

export interface ChordHint {
  startSec: number;
  endSec: number;
  chord: string;
  confidence: number;
  quality: "high" | "medium" | "low";
}

export interface StructureSection {
  startSec: number;
  endSec: number;
  label: "intro" | "verse" | "pre_chorus" | "chorus" | "bridge" | "interlude" | "outro" | "unknown";
  confidence: number;
  reason: string | null;
}

export type InstrumentLabel =
  | "piano"
  | "strings"
  | "cello_low_strings"
  | "violin_high_strings"
  | "electric_bass"
  | "drum_kit"
  | "percussion"
  | "synth"
  | "acoustic_guitar"
  | "vocal";

export interface InstrumentHint {
  label: InstrumentLabel;
  confidence: number;
  source: string;
  evidence: string[];
  visible: boolean;
}

export interface AudioFeatureSummary {
  rms: number | null;
  peak: number | null;
  silenceRatio: number | null;
  lowEnergyRatio: number | null;
  midEnergyRatio: number | null;
  highEnergyRatio: number | null;
  spectralCentroid: number | null;
  spectralRolloff: number | null;
  spectralFlatness: number | null;
  zeroCrossingRate: number | null;
  onsetDensity: number | null;
  transientStrength: number | null;
}

export interface AudioVisualizationData {
  waveform: number[];
  spectrum: number[];
}

export interface StemInsight {
  features: AudioFeatureSummary;
  visualization: AudioVisualizationData;
  instrumentHints: InstrumentHint[];
}
