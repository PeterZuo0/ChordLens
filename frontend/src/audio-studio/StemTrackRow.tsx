import { getApiAssetUrl } from "../api/client";
import type { StemName } from "../api/types";
import { formatConfidence, visibleInstrumentHints } from "./analysisFormatting";
import { labelText } from "./InstrumentEvidenceList";
import type { StemTrackState } from "./stemPlayback";
import { WaveformPreview } from "./WaveformPreview";

interface StemTrackRowProps {
  track: StemTrackState;
  audibleVolume: number;
  onMute: (name: StemName) => void;
  onSolo: (name: StemName) => void;
  onVolume: (name: StemName, volume: number) => void;
}

const stemLabels: Record<StemName, string> = {
  vocals: "Vocals",
  drums: "Drums",
  bass: "Bass",
  other: "Other",
  piano: "Piano",
  strings: "Strings"
};

export function StemTrackRow({ track, audibleVolume, onMute, onSolo, onVolume }: StemTrackRowProps) {
  const analysis = track.item.analysis;
  const hints = analysis ? visibleInstrumentHints(analysis.instrumentHints).slice(0, 2) : [];

  return (
    <div className="stem-console-row">
      <div className="stem-meter" aria-hidden="true">
        <span style={{ height: `${Math.max(8, audibleVolume * 100)}%` }} />
      </div>
      <div className="stem-track-copy">
        <strong>{stemLabels[track.name]}</strong>
        <small>{formatStemDetail(track.item.fileSizeBytes, track.item.format)}</small>
        {hints.length > 0 ? (
          <div className="stem-mini-tags">
            {hints.map((hint) => (
              <span key={hint.label}>
                {labelText(hint.label)} {formatConfidence(hint.confidence)}
              </span>
            ))}
          </div>
        ) : null}
      </div>
      {analysis ? (
        <WaveformPreview
          compact
          label={`${stemLabels[track.name]} waveform`}
          spectrum={analysis.visualization.spectrum}
          waveform={analysis.visualization.waveform}
        />
      ) : null}
      <div className="stem-row-actions" aria-label={`${stemLabels[track.name]} stem controls`}>
        <button
          aria-pressed={track.muted}
          className={track.muted ? "icon-button active danger" : "icon-button"}
          onClick={() => onMute(track.name)}
          type="button"
        >
          M
        </button>
        <button
          aria-pressed={track.soloed}
          className={track.soloed ? "icon-button active" : "icon-button"}
          onClick={() => onSolo(track.name)}
          type="button"
        >
          S
        </button>
      </div>
      <label className="stem-volume">
        <span>{Math.round(track.volume * 100)}%</span>
        <input
          aria-label={`${stemLabels[track.name]} volume`}
          max="1"
          min="0"
          onChange={(event) => onVolume(track.name, Number(event.target.value))}
          step="0.01"
          type="range"
          value={track.volume}
        />
      </label>
      {track.item.downloadUrl ? (
        <a className="stem-download" href={getApiAssetUrl(track.item.downloadUrl)} rel="noreferrer">
          WAV
        </a>
      ) : (
        <span className="stem-download disabled">WAV</span>
      )}
    </div>
  );
}

function formatStemDetail(bytes: number | null, format: string | null) {
  const size = bytes ? formatSize(bytes) : "size unknown";
  return `${format?.toUpperCase() ?? "AUDIO"} / ${size}`;
}

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
