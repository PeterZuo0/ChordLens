import type { ChordLoopEvent } from "./types";

interface ChordTimelineProps {
  events: ChordLoopEvent[];
}

export function ChordTimeline({ events }: ChordTimelineProps) {
  return (
    <section className="tool-panel loop-timeline">
      <div className="panel-heading">
        <span className="panel-label">Loop timeline</span>
        <strong>{events.length} events</strong>
      </div>
      {events.length ? (
        <div className="loop-events">
          {events.map((event, index) => (
            <div className="loop-event" key={event.id}>
              <span>{index + 1}</span>
              <strong>
                {event.chord} x{event.beats}
              </strong>
              <small>{new Date(event.createdAt).toLocaleTimeString()}</small>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">Choose a beat length and chord, then commit the first event.</p>
      )}
    </section>
  );
}
