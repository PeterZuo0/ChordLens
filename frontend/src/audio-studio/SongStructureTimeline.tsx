import type { TransientAudioAnalysisResponse } from "../api/types";
import { buildStructureSegments, confidenceTone, formatTimeRange, sectionLabel } from "./audioInsights";

interface SongStructureTimelineProps {
  sections: TransientAudioAnalysisResponse["music"]["structure"];
  durationSec: number | null;
}

export function SongStructureTimeline({ sections, durationSec }: SongStructureTimelineProps) {
  const segments = buildStructureSegments(sections);

  return (
    <section className="tool-panel structure-timeline a1-motion-item">
      <div className="panel-heading">
        <span className="panel-label">Song Structure</span>
        <strong>Best-effort arrangement map</strong>
        <span className="panel-meta">{durationSec ? `${Math.round(durationSec)}s source` : "duration unknown"}</span>
      </div>
      {segments.length > 0 ? (
        <>
          <div className="structure-track" aria-label="Song structure timeline">
            {segments.map((segment, index) => (
              <div
                className={`structure-segment ${confidenceTone(segment.confidence)}`}
                key={`${segment.label}-${segment.startSec}-${index}`}
                style={{ left: `${segment.left}%`, width: `${segment.width}%` }}
              >
                <span className="structure-segment-label">{sectionLabel(segment.label)}</span>
                <small>{formatTimeRange(segment.startSec, segment.endSec)}</small>
              </div>
            ))}
          </div>
          <div className="structure-meta">
            {segments.map((segment, index) => (
              <span key={`${segment.label}-meta-${index}`}>
                {sectionLabel(segment.label)} {formatTimeRange(segment.startSec, segment.endSec)}
              </span>
            ))}
          </div>
        </>
      ) : (
        <p className="muted">No song structure sections returned for this analysis.</p>
      )}
    </section>
  );
}
