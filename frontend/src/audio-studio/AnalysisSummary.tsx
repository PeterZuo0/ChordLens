import type { TransientAudioAnalysisResponse } from "../api/types";

interface AnalysisSummaryProps {
  analysis: TransientAudioAnalysisResponse | null;
}

function formatDuration(durationSec: number | null) {
  if (durationSec === null) {
    return "Unknown";
  }
  return `${durationSec.toFixed(1)}s`;
}

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function AnalysisSummary({ analysis }: AnalysisSummaryProps) {
  return (
    <section className="tool-panel">
      <div className="panel-heading">
        <span className="panel-label">Analysis</span>
        <strong>{analysis?.analysisKind ?? "No result"}</strong>
      </div>
      {analysis ? (
        <>
          <div className="summary-grid">
            <div>
              <span>Source</span>
              <strong>{analysis.source.fileName}</strong>
            </div>
            <div>
              <span>Format</span>
              <strong>{analysis.source.format}</strong>
            </div>
            <div>
              <span>Size</span>
              <strong>{formatSize(analysis.source.fileSizeBytes)}</strong>
            </div>
            <div>
              <span>Duration</span>
              <strong>{formatDuration(analysis.source.durationSec)}</strong>
            </div>
            <div>
              <span>Sample rate</span>
              <strong>{analysis.source.sampleRate ? `${analysis.source.sampleRate} Hz` : "Unknown"}</strong>
            </div>
            <div>
              <span>Channels</span>
              <strong>{analysis.source.channels ?? "Unknown"}</strong>
            </div>
            <div>
              <span>BPM</span>
              <strong>{analysis.music.bpm ?? "Unknown"}</strong>
            </div>
            <div>
              <span>Key</span>
              <strong>{analysis.music.key ?? "Unknown"}</strong>
            </div>
          </div>
          <p className="status-note">
            This result is best-effort and temporary. Refreshing the page clears it.
          </p>
        </>
      ) : (
        <p className="muted">Upload a local audio file to run one-time analysis.</p>
      )}
    </section>
  );
}
