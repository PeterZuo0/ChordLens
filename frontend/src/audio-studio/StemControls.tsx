import type { TransientAudioAnalysisResponse } from "../api/types";
import { WorkspacePanel } from "../components/WorkspacePanel";

interface StemControlsProps {
  stems: TransientAudioAnalysisResponse["stems"] | null;
}

export function StemControls({ stems }: StemControlsProps) {
  const heading = stems?.requested ? stems.status : "not_requested";

  return (
    <WorkspacePanel className="stem-panel" label="Stems" title={heading}>
      {!stems || stems.status === "not_requested" ? (
        <p className="muted">Stem separation was not requested.</p>
      ) : null}
      {stems?.status === "unavailable" ? (
        <p className="muted">{stems.message ?? "Stem separation is unavailable on this machine."}</p>
      ) : null}
      {stems?.status === "failed" ? (
        <p className="error-text">{stems.message ?? "Stem separation failed."}</p>
      ) : null}
      {stems?.status === "complete" ? (
        <>
          <div className="stem-list">
            {stems.items.map((stem) => (
              <div className="stem-row" key={stem.name}>
                <span>{stem.name}</span>
                <small>Separated temporarily</small>
              </div>
            ))}
          </div>
          <p className="muted">Stem files were temporary, so playback controls are not available in this iteration.</p>
        </>
      ) : null}
    </WorkspacePanel>
  );
}
