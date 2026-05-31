import type { TransientAudioAnalysisResponse } from "../api/types";
import { formatConfidence, visibleInstrumentHints } from "./analysisFormatting";
import { confidenceTone, formatEvidence, getVisibleAndTechnicalHints } from "./audioInsights";
import { labelText } from "./InstrumentEvidenceList";

interface StemInsightPanelProps {
  items: TransientAudioAnalysisResponse["stems"]["items"];
}

const stemLabels: Record<string, string> = {
  vocals: "Vocals",
  drums: "Drums",
  bass: "Bass",
  other: "Other",
  piano: "Piano",
  strings: "Strings"
};

export function StemInsightPanel({ items }: StemInsightPanelProps) {
  const analyzedItems = items.filter((item) => item.analysis);

  if (analyzedItems.length === 0) {
    return <p className="muted">No per-stem analysis returned for this session.</p>;
  }

  return (
    <section className="stem-insight-panel a1-motion-item" aria-label="Per-stem instrument insight">
      {analyzedItems.map((item) => {
        const analysis = item.analysis;
        if (!analysis) {
          return null;
        }
        const visible = visibleInstrumentHints(analysis.instrumentHints).slice(0, 3);
        const { technical } = getVisibleAndTechnicalHints(analysis.instrumentHints);
        return (
          <article className="stem-insight-row" key={item.name}>
            <div className="stem-insight-title">
              <span className="panel-label">{stemLabels[item.name]}</span>
              <strong>{visible.length > 0 ? visible.map((hint) => labelText(hint.label)).join(" / ") : "No visible hint"}</strong>
            </div>
            <div className="stem-insight-tags">
              {visible.map((hint) => (
                <span className={confidenceTone(hint.confidence)} key={`${item.name}-${hint.label}`}>
                  {labelText(hint.label)} {formatConfidence(hint.confidence)}
                </span>
              ))}
              <span>RMS {metric(analysis.features.rms)}</span>
              <span>Onsets {metric(analysis.features.onsetDensity)}</span>
              <span>Low {formatConfidence(analysis.features.lowEnergyRatio)}</span>
            </div>
            {technical.length > 0 ? (
              <details className="technical-hints compact">
                <summary>Technical hints</summary>
                <div className="instrument-evidence-tags">
                  {technical.flatMap((hint) => formatEvidence(hint.evidence).slice(0, 2)).map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
              </details>
            ) : null}
          </article>
        );
      })}
    </section>
  );
}

function metric(value: number | null) {
  return value === null ? "Unknown" : value.toFixed(2);
}
