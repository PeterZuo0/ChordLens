import type { TransientAudioAnalysisResponse } from "../api/types";
import { MetricTile } from "../components/MetricTile";
import { WorkspacePanel } from "../components/WorkspacePanel";
import { InstrumentEvidenceList } from "./InstrumentEvidenceList";
import { TempoConfidencePanel } from "./TempoConfidencePanel";
import { WaveformPreview } from "./WaveformPreview";

interface AnalysisSummaryProps {
  analysis: TransientAudioAnalysisResponse | null;
}

function formatDuration(durationSec: number | null) {
  if (durationSec === null) {
    return "Unknown";
  }
  const minutes = Math.floor(durationSec / 60);
  const seconds = Math.round(durationSec % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function AnalysisSummary({ analysis }: AnalysisSummaryProps) {
  return (
    <WorkspacePanel className="analysis-panel" label="Analysis" title={analysis?.analysisKind ?? "No result"}>
      {analysis ? (
        <>
          <div className="summary-grid">
            <MetricTile detail={analysis.source.fileName} label="Source" tone="cool" value="Loaded" />
            <MetricTile label="Format" value={analysis.source.format} />
            <MetricTile label="Size" value={formatSize(analysis.source.fileSizeBytes)} />
            <MetricTile label="Duration" value={formatDuration(analysis.source.durationSec)} />
            <MetricTile
              label="Sample rate"
              value={analysis.source.sampleRate ? `${analysis.source.sampleRate} Hz` : "Unknown"}
            />
            <MetricTile label="Channels" value={analysis.source.channels ? `${analysis.source.channels} CH` : "Unknown"} />
          </div>
          <TempoConfidencePanel music={analysis.music} />
          <WaveformPreview
            label="Source waveform"
            spectrum={analysis.music.visualization.spectrum}
            waveform={analysis.music.visualization.waveform}
          />
          <div className="analysis-instrument-summary">
            <span className="panel-label">Full-mix instruments</span>
            <InstrumentEvidenceList hints={analysis.music.instrumentSummary} />
          </div>
          <p className="status-note">
            This result is best-effort and temporary. Refreshing the page clears it.
          </p>
        </>
      ) : (
        <p className="muted">Upload a local audio file to run one-time analysis.</p>
      )}
    </WorkspacePanel>
  );
}
