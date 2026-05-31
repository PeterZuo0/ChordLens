import type { BeatLength, ChordName } from "./types";

interface ArControlsProps {
  selectedBeat: BeatLength;
  selectedChord: ChordName;
  onBeatChange: (beat: BeatLength) => void;
  onChordChange: (chord: ChordName) => void;
  onCommit: () => void;
  onUndo: () => void;
  onClear: () => void;
}

const beats: BeatLength[] = [1, 2, 4, 8];
const chords: ChordName[] = ["C", "D", "E", "F", "G", "A", "B"];

export function ArControls({
  selectedBeat,
  selectedChord,
  onBeatChange,
  onChordChange,
  onCommit,
  onUndo,
  onClear
}: ArControlsProps) {
  return (
    <section className="ar-controls-layout" aria-label="Manual loop input">
      <div className="tool-panel beat-rail">
        <div className="panel-heading">
          <span className="panel-label">Left hand</span>
          <strong>Beats</strong>
        </div>
        <div className="segmented-grid rail-grid">
          {beats.map((beat) => (
            <button
              aria-pressed={selectedBeat === beat}
              className={selectedBeat === beat ? "selected" : ""}
              key={beat}
              onClick={() => onBeatChange(beat)}
              type="button"
            >
              <strong>{beat}</strong>
              <span>beats</span>
            </button>
          ))}
        </div>
      </div>

      <div className="tool-panel chord-rail">
        <div className="panel-heading">
          <span className="panel-label">Right hand</span>
          <strong>Chord</strong>
        </div>
        <div className="chord-grid rail-grid">
          {chords.map((chord) => (
            <button
              aria-pressed={selectedChord === chord}
              className={selectedChord === chord ? "selected" : ""}
              key={chord}
              onClick={() => onChordChange(chord)}
              type="button"
            >
              {chord}
            </button>
          ))}
        </div>
        <p className="muted rail-note">Minor and seventh variants are planned after the root-note loop works.</p>
      </div>

      <div className="tool-panel transport-actions">
        <span className="panel-label">Manual commit</span>
        <button className="button primary" onClick={onCommit} type="button">
          Commit chord
        </button>
        <button className="button secondary" onClick={onUndo} type="button">
          Undo
        </button>
        <button className="button secondary" onClick={onClear} type="button">
          Clear
        </button>
      </div>
    </section>
  );
}
