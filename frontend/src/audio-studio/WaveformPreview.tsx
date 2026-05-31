import { makeSpectrumBars, makeWaveformPath } from "./audioInsights";

interface WaveformPreviewProps {
  waveform: number[] | null | undefined;
  spectrum: number[] | null | undefined;
  label: string;
  compact?: boolean;
}

const width = 240;
const height = 54;
const spectrumHeight = 26;

export function WaveformPreview({ waveform, spectrum, label, compact = false }: WaveformPreviewProps) {
  const waveformValues = waveform ?? [];
  const spectrumValues = spectrum ?? [];
  const waveformPath = makeWaveformPath(waveformValues, width, height);
  const spectrumBars = makeSpectrumBars(spectrumValues.slice(0, compact ? 36 : 56), width, spectrumHeight);
  const hasWaveform = waveformPath.length > 0;
  const hasSpectrum = spectrumBars.length > 0;

  return (
    <div className={compact ? "waveform-preview compact" : "waveform-preview"}>
      <div className="waveform-meta">
        <span>{label}</span>
        <small>{hasWaveform ? `${waveformValues.length} real peaks` : "No waveform data"}</small>
      </div>
      {hasWaveform || hasSpectrum ? (
        <svg
          aria-label={`${label} real waveform preview`}
          className="waveform-svg"
          focusable="false"
          role="img"
          viewBox={`0 0 ${width} ${height + spectrumHeight + 8}`}
        >
          <line className="waveform-midline" x1="0" x2={width} y1={height / 2} y2={height / 2} />
          {waveformValues.map((value, index) => {
            const x = waveformValues.length === 1 ? 0 : (index / (waveformValues.length - 1)) * width;
            const barHeight = Math.max(1, Math.min(1, Math.max(0, value)) * (height - 8));
            return (
              <line
                className="waveform-peak"
                key={`${index}-${value}`}
                x1={x}
                x2={x}
                y1={height / 2 - barHeight / 2}
                y2={height / 2 + barHeight / 2}
              />
            );
          })}
          <path className="waveform-line" d={waveformPath} />
          <g className="spectrum-bars" transform={`translate(0 ${height + 8})`}>
            {spectrumBars.map((bar, index) => (
              <rect key={`${index}-${bar.x}`} height={bar.height} width={bar.width} x={bar.x} y={bar.y} />
            ))}
          </g>
        </svg>
      ) : (
        <div className="waveform-empty">No real waveform data returned.</div>
      )}
    </div>
  );
}
