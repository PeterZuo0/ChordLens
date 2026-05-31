import type { InstrumentHint, TempoCandidate } from "../api/types";

interface TempoLike {
  bpm: number | null;
  bpmCandidates: TempoCandidate[];
}

export function formatConfidence(value: number | null) {
  if (value === null || Number.isNaN(value)) {
    return "Unknown";
  }
  return `${Math.round(Math.max(0, Math.min(1, value)) * 100)}%`;
}

export function getPrimaryTempoLabel(music: TempoLike) {
  const bpm = music.bpm ?? music.bpmCandidates[0]?.bpm ?? null;
  return bpm === null ? "Unknown" : `${bpm} BPM`;
}

export function sortInstrumentHints<T extends Pick<InstrumentHint, "confidence" | "label">>(hints: T[]) {
  return [...hints].sort((left, right) => right.confidence - left.confidence || left.label.localeCompare(right.label));
}

export function visibleInstrumentHints(hints: InstrumentHint[]) {
  return sortInstrumentHints(hints.filter((hint) => hint.visible));
}
