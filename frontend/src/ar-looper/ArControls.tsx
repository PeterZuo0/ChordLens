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
    <section className="tool-panel ar-control-panel">
      <div className="panel-heading">
        <span className="panel-label">Manual loop input</span>
        <strong>
          {selectedChord} x{selectedBeat}
        </strong>
      </div>
      <div className="control-group">
        <span>Beats</span>
        <div className="segmented-grid">
          {beats.map((beat) => (
            <button
              aria-pressed={selectedBeat === beat}
              className={selectedBeat === beat ? "selected" : ""}
              key={beat}
              onClick={() => onBeatChange(beat)}
              type="button"
            >
              {beat}
            </button>
          ))}
        </div>
      </div>
      <div className="control-group">
        <span>Chord</span>
        <div className="chord-grid">
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
      </div>
      <div className="button-row">
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
