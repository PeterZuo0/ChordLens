import type { InstrumentHint } from "../api/types";
import { formatConfidence } from "./analysisFormatting";
import { formatEvidence, getVisibleAndTechnicalHints } from "./audioInsights";

interface InstrumentEvidenceListProps {
  hints: InstrumentHint[];
  compact?: boolean;
}

export function InstrumentEvidenceList({ hints, compact = false }: InstrumentEvidenceListProps) {
  const { visible, technical } = getVisibleAndTechnicalHints(hints);

  if (hints.length === 0) {
    return <p className="muted">No instrument hints returned for this analysis.</p>;
  }

  return (
    <div className={compact ? "instrument-evidence compact" : "instrument-evidence"}>
      <div className="instrument-evidence-list">
        {visible.map((hint) => (
          <InstrumentHintCard hint={hint} key={`${hint.label}-${hint.source}`} />
        ))}
      </div>
      {technical.length > 0 ? (
        <details className="technical-hints">
          <summary>Technical low-confidence hints ({technical.length})</summary>
          <div className="instrument-evidence-list">
            {technical.map((hint) => (
              <InstrumentHintCard hint={hint} key={`${hint.label}-${hint.source}`} />
            ))}
          </div>
        </details>
      ) : null}
    </div>
  );
}

function InstrumentHintCard({ hint }: { hint: InstrumentHint }) {
  const evidence = formatEvidence(hint.evidence);

  return (
    <article className="instrument-card">
      <div>
        <strong>{labelText(hint.label)}</strong>
        <span>{formatConfidence(hint.confidence)}</span>
      </div>
      <small>source {hint.source}</small>
      {evidence.length > 0 ? (
        <div className="instrument-evidence-tags">
          {evidence.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      ) : null}
    </article>
  );
}

export function labelText(label: string) {
  return label
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
