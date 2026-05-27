import type { ChordEvent } from "../api/types";

interface ChordTimelineProps {
  chords: ChordEvent[];
}

export function ChordTimeline({ chords }: ChordTimelineProps) {
  return (
    <section className="tool-panel">
      <div className="panel-heading">
        <span className="panel-label">Chord timeline</span>
        <strong>{chords.length} events</strong>
      </div>
      {chords.length ? (
        <div className="timeline-strip">
          {chords.map((event) => (
            <div className="timeline-event" key={`${event.timeSec}-${event.chord}`}>
              <span>{event.timeSec.toFixed(0)}s</span>
              <strong>{event.chord}</strong>
              <small>{event.confidence === null ? "mock" : `${Math.round(event.confidence * 100)}%`}</small>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">No chord events yet.</p>
      )}
    </section>
  );
}
