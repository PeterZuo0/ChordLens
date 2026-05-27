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
