import { useRef, useState } from "react";

import { getApiAssetUrl } from "../api/client";
import type { TransientAudioAnalysisResponse } from "../api/types";
import { WorkspacePanel } from "../components/WorkspacePanel";
import { getStemAudibleVolume } from "./stemPlayback";
import { StemInsightPanel } from "./StemInsightPanel";
import { StemTrackRow } from "./StemTrackRow";
import { StemTransport } from "./StemTransport";
import { useStemPlayback } from "./useStemPlayback";

interface StemReviewConsoleProps {
  processing: boolean;
  stems: TransientAudioAnalysisResponse["stems"] | null;
  onClearSession: (sessionId: string) => Promise<void>;
  onRetry: () => Promise<void>;
}

export function StemReviewConsole({ processing, stems, onClearSession, onRetry }: StemReviewConsoleProps) {
  if (processing) {
    return (
      <WorkspacePanel className="stem-review-console processing" label="Stem Review" title="Demucs processing">
        <div className="stem-state-visual" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
        </div>
        <p className="muted">Separating vocals, drums, bass, other, piano, and strings locally. This can take several minutes.</p>
      </WorkspacePanel>
    );
  }

  if (!stems || stems.status === "not_requested") {
    return (
      <WorkspacePanel className="stem-review-console" label="Stem Review" title="No stem session">
        <p className="muted">Enable Separate stems before analyzing to generate local Demucs tracks.</p>
      </WorkspacePanel>
    );
  }

  if (stems.status === "unavailable") {
    return (
      <WorkspacePanel className="stem-review-console unavailable" label="Stem Review" title="Demucs unavailable">
        <p className="muted">{stems.message ?? "Demucs is not available on this machine."}</p>
        <button className="button secondary" onClick={onRetry} type="button">
          Retry analysis
        </button>
      </WorkspacePanel>
    );
  }

  if (stems.status === "failed") {
    return (
      <WorkspacePanel className="stem-review-console failed" label="Stem Review" title="Stem separation failed">
        <p className="error-text">{stems.message ?? "Demucs stem separation failed."}</p>
        <button className="button secondary" onClick={onRetry} type="button">
          Retry Demucs
        </button>
      </WorkspacePanel>
    );
  }

  return <CompleteStemConsole stems={stems} onClearSession={onClearSession} onRetry={onRetry} />;
}

interface CompleteStemConsoleProps {
  stems: TransientAudioAnalysisResponse["stems"];
  onClearSession: (sessionId: string) => Promise<void>;
  onRetry: () => Promise<void>;
}

function CompleteStemConsole({ stems, onClearSession, onRetry }: CompleteStemConsoleProps) {
  const playableItems = stems.items.filter((item) => item.streamUrl);
  const playback = useStemPlayback(playableItems);
  const clearingRef = useRef(false);
  const [isClearing, setIsClearing] = useState(false);

  async function clearSession() {
    if (!stems.sessionId || clearingRef.current) {
      return;
    }
    clearingRef.current = true;
    setIsClearing(true);
    playback.unload();
    try {
      await onClearSession(stems.sessionId);
    } finally {
      clearingRef.current = false;
      setIsClearing(false);
    }
  }

  return (
    <WorkspacePanel className="stem-review-console complete" label="Stem Review" title={`${stems.items.length}-track stem session`}>
      <div className="stem-console-toolbar">
        <div>
          <span className="panel-label">Engine</span>
          <strong>{stems.engine ?? "demucs"}</strong>
        </div>
        <div className="stem-session-actions">
          {stems.zipDownloadUrl ? (
            <a className="button secondary" href={getApiAssetUrl(stems.zipDownloadUrl)}>
              Download ZIP
            </a>
          ) : null}
          <button className="button secondary" onClick={onRetry} type="button">
            Retry
          </button>
          {stems.sessionId ? (
            <button
              className="button secondary danger"
              disabled={isClearing}
              onClick={() => void clearSession()}
              onMouseDown={() => void clearSession()}
              type="button"
            >
              {isClearing ? "Clearing..." : "Clear"}
            </button>
          ) : null}
        </div>
      </div>

      <StemTransport
        currentTime={playback.currentTime}
        duration={playback.duration}
        isPlaying={playback.isPlaying}
        onPause={playback.pause}
        onPlay={playback.play}
        onSeek={playback.seek}
      />

      <StemInsightPanel items={stems.items} />

      <div className="stem-console-list">
        {playback.tracks.map((track) => (
          <StemTrackRow
            audibleVolume={getStemAudibleVolume(playback.tracks, track.name)}
            key={track.name}
            onMute={playback.toggleMute}
            onSolo={playback.toggleSolo}
            onVolume={playback.setVolume}
            track={track}
          />
        ))}
      </div>

      {playback.playbackError ? <p className="error-text">{playback.playbackError}</p> : null}

      <div className="stem-audio-bank" aria-hidden="true">
        {playableItems.map((item) => (
          <audio
            key={item.name}
            onDurationChange={playback.syncMediaState}
            onEnded={playback.syncMediaState}
            onTimeUpdate={playback.syncMediaState}
            preload="metadata"
            ref={(node) => playback.registerAudio(item.name, node)}
            src={item.streamUrl ? getApiAssetUrl(item.streamUrl) : undefined}
          />
        ))}
      </div>
    </WorkspacePanel>
  );
}
