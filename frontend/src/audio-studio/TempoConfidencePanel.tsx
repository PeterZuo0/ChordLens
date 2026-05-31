import type { TransientAudioAnalysisResponse } from "../api/types";
import { formatConfidence, getPrimaryTempoLabel } from "./analysisFormatting";

interface TempoConfidencePanelProps {
  music: TransientAudioAnalysisResponse["music"];
}

export function TempoConfidencePanel({ music }: TempoConfidencePanelProps) {
  return (
    <div className="tempo-confidence-panel">
      <div className="tempo-primary">
        <span>BPM estimate</span>
        <strong>{getPrimaryTempoLabel(music)}</strong>
        <small>Confidence {formatConfidence(music.bpmConfidence)}</small>
      </div>
      <div className="tempo-primary accent">
        <span>Key estimate</span>
        <strong>{music.key ?? "Unknown"}</strong>
        <small>Confidence {formatConfidence(music.keyConfidence)}</small>
      </div>
      <div className="tempo-candidates">
        <span className="panel-label">Tempo candidates</span>
        {music.bpmCandidates.length > 0 ? (
          <div className="tempo-candidate-list">
            {music.bpmCandidates.slice(0, 3).map((candidate) => (
              <span key={`${candidate.bpm}-${candidate.source}`}>
                <strong>{candidate.bpm}</strong>
                <small>{formatConfidence(candidate.confidence)}</small>
              </span>
            ))}
          </div>
        ) : (
          <p className="muted">No stable tempo candidates returned.</p>
        )}
      </div>
      {music.bpmMessage ? <p className="status-note compact">{music.bpmMessage}</p> : null}
    </div>
  );
}
