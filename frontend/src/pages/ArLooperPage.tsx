import { useState } from "react";

import { ArControls } from "../ar-looper/ArControls";
import { ChordTimeline } from "../ar-looper/ChordTimeline";
import { playChordPreview } from "../ar-looper/synth";
import type { BeatLength, ChordLoopEvent, ChordName } from "../ar-looper/types";
import { AppShell } from "../app/AppShell";
import { routes } from "../app/routes";

export function ArLooperPage() {
  const [selectedBeat, setSelectedBeat] = useState<BeatLength>(2);
  const [selectedChord, setSelectedChord] = useState<ChordName>("G");
  const [events, setEvents] = useState<ChordLoopEvent[]>([]);

  function commitEvent() {
    // Future hand tracking should feed this same commit boundary after hover stabilization.
    const event: ChordLoopEvent = {
      id: crypto.randomUUID(),
      chord: selectedChord,
      beats: selectedBeat,
      createdAt: new Date().toISOString()
    };
    setEvents((current) => [...current, event]);
    playChordPreview(selectedChord);
  }

  return (
    <AppShell
      activeRoute={routes.arLooper}
      statusItems={[
        { label: "Input", value: "Manual", tone: "warn" },
        { label: "Synth", value: "Preview active", tone: "ok" },
        { label: "Tracking", value: "Adapter pending", tone: "muted" }
      ]}
    >
      <header className="workspace-header">
        <div>
          <span className="panel-label">AR Looper</span>
          <h1>AR Chord Looper</h1>
          <p>Manual chord commits prove the loop boundary before MediaPipe hand tracking is connected.</p>
        </div>
        <span className="phase-tag">Phase 2B manual input</span>
      </header>

      <div className="ar-console">
        <section className="transport-strip" aria-label="Looper transport">
          <div>
            <span className="panel-label">Current selection</span>
            <strong>
              {selectedChord} x{selectedBeat}
            </strong>
          </div>
          <div className="transport-metrics">
            <span>Commit threshold 300ms</span>
            <span>Cooldown 500ms</span>
            <span>Local synth preview</span>
          </div>
        </section>

        <section className="camera-stage">
          <div className="camera-frame">
            <div className="tracking-badges" aria-label="Planned hand tracking states">
              <span>hover</span>
              <span className="armed">armed</span>
              <span className="committed">committed</span>
              <span>cooldown</span>
            </div>
            <span>Camera preview placeholder</span>
            <strong>
              {selectedChord} x{selectedBeat}
            </strong>
            <small>Manual input active. Hand tracking adapter is not connected in this increment.</small>
          </div>
        </section>

        <ArControls
          onBeatChange={setSelectedBeat}
          onChordChange={setSelectedChord}
          onClear={() => setEvents([])}
          onCommit={commitEvent}
          onUndo={() => setEvents((current) => current.slice(0, -1))}
          selectedBeat={selectedBeat}
          selectedChord={selectedChord}
        />
        <ChordTimeline events={events} />
      </div>
    </AppShell>
  );
}
