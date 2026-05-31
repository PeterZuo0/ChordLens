import type { TransientAudioAnalysisResponse } from "../api/types";
import { formatConfidence } from "./analysisFormatting";
import { formatTimeRange } from "./audioInsights";

interface ChordHintTimelineProps {
  hints: TransientAudioAnalysisResponse["music"]["chordHints"];
}

export function ChordHintTimeline({ hints }: ChordHintTimelineProps) {
  return (
    <section className="tool-panel chord-hint-timeline a1-motion-item">
      <div className="panel-heading">
        <span className="panel-label">Chord Hints</span>
        <strong>Best-effort harmonic cues</strong>
        <span className="panel-meta">{hints.length} hints</span>
      </div>
      {hints.length > 0 ? (
        <div className="chord-hint-list">
          {hints.slice(0, 24).map((hint) => (
            <span className={`chord-hint-chip ${hint.quality}`} key={`${hint.startSec}-${hint.chord}`}>
              <strong>{hint.chord}</strong>
              <small>
                {formatTimeRange(hint.startSec, hint.endSec)} / {formatConfidence(hint.confidence)}
              </small>
            </span>
          ))}
        </div>
      ) : (
        <p className="muted">No confident chord hints returned for this analysis.</p>
      )}
    </section>
  );
}
