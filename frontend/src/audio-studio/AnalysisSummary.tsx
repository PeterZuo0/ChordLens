import type { AnalysisSummary as AnalysisSummaryType, ProjectSummary } from "../api/types";

interface AnalysisSummaryProps {
  project: ProjectSummary | null;
  analysis: AnalysisSummaryType | null;
}

export function AnalysisSummary({ project, analysis }: AnalysisSummaryProps) {
  return (
    <section className="tool-panel">
      <div className="panel-heading">
        <span className="panel-label">Analysis</span>
        <strong>{analysis?.analysisKind ?? "No project"}</strong>
      </div>
      {project && analysis ? (
        <div className="summary-grid">
          <div>
            <span>Project</span>
            <strong>{project.title}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{project.status}</strong>
          </div>
          <div>
            <span>BPM</span>
            <strong>{analysis.bpm}</strong>
          </div>
          <div>
            <span>Key</span>
            <strong>{analysis.key}</strong>
          </div>
          <div>
            <span>Duration</span>
            <strong>{analysis.durationSec ? `${analysis.durationSec}s` : "Unknown"}</strong>
          </div>
          <div>
            <span>Source</span>
            <strong>{project.sourceFileName ?? "Mock project"}</strong>
          </div>
        </div>
      ) : (
        <p className="muted">Create or upload a local audio project to view mock analysis.</p>
      )}
    </section>
  );
}
