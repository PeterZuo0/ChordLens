interface StemControlsProps {
  stems: string[];
}

export function StemControls({ stems }: StemControlsProps) {
  const visibleStems = stems.length ? stems : ["vocals", "drums", "bass", "other"];

  return (
    <section className="tool-panel">
      <div className="panel-heading">
        <span className="panel-label">Stems</span>
        <strong>Placeholder controls</strong>
      </div>
      <div className="stem-list">
        {visibleStems.map((stem) => (
          <div className="stem-row" key={stem}>
            <span>{stem}</span>
            <div className="stem-actions">
              <button disabled type="button">
                Solo
              </button>
              <button disabled type="button">
                Mute
              </button>
            </div>
          </div>
        ))}
      </div>
      <p className="muted">Real stem playback and vocal removal are not connected yet.</p>
    </section>
  );
}
