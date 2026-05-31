import type { InstrumentHint, StructureSection } from "../api/types";
import { sortInstrumentHints } from "./analysisFormatting";

export interface StructureSegment extends StructureSection {
  left: number;
  width: number;
}

export interface SpectrumBar {
  height: number;
  width: number;
  x: number;
  y: number;
}

export type ConfidenceTone = "high" | "medium" | "low";

const sectionLabels: Record<StructureSection["label"], string> = {
  intro: "Intro",
  verse: "Verse",
  pre_chorus: "Pre-chorus",
  chorus: "Chorus",
  bridge: "Bridge",
  interlude: "Interlude",
  outro: "Outro",
  unknown: "Unknown"
};

export function buildStructureSegments(sections: StructureSection[]): StructureSegment[] {
  if (sections.length === 0) {
    return [];
  }

  const start = Math.min(...sections.map((section) => section.startSec));
  const end = Math.max(...sections.map((section) => section.endSec));
  const duration = Math.max(0.001, end - start);

  return sections.map((section) => ({
    ...section,
    left: clampPercent(((section.startSec - start) / duration) * 100),
    width: Math.max(2, clampPercent(((section.endSec - section.startSec) / duration) * 100))
  }));
}

export function sectionLabel(label: StructureSection["label"]) {
  return sectionLabels[label] ?? titleCase(label.replace(/_/g, " "));
}

export function getVisibleAndTechnicalHints(hints: InstrumentHint[]) {
  const sorted = sortInstrumentHints(hints);
  return {
    visible: sorted.filter((hint) => hint.visible),
    technical: sorted.filter((hint) => !hint.visible)
  };
}

export function makeWaveformPath(values: number[], width: number, height: number) {
  const clean = values.map(clampUnit).filter((value) => Number.isFinite(value));
  if (clean.length === 0 || width <= 0 || height <= 0) {
    return "";
  }
  if (clean.length === 1) {
    const y = centerY(clean[0], height);
    return `M 0 ${round(y)} L ${round(width)} ${round(y)}`;
  }

  const step = width / (clean.length - 1);
  return clean
    .map((value, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command} ${round(index * step)} ${round(centerY(value, height))}`;
    })
    .join(" ");
}

export function makeSpectrumBars(values: number[], width: number, height: number): SpectrumBar[] {
  const clean = values.map(clampUnit).filter((value) => Number.isFinite(value));
  if (clean.length === 0 || width <= 0 || height <= 0) {
    return [];
  }

  const gap = clean.length > 24 ? 1 : 2;
  const barWidth = Math.max(1, (width - gap * (clean.length - 1)) / clean.length);
  return clean.map((value, index) => {
    const barHeight = Math.max(1, value * height);
    return {
      height: round(barHeight),
      width: round(barWidth),
      x: round(index * (barWidth + gap)),
      y: round(height - barHeight)
    };
  });
}

export function confidenceTone(confidence: number | null): ConfidenceTone {
  if (confidence !== null && confidence >= 0.66) {
    return "high";
  }
  if (confidence !== null && confidence >= 0.35) {
    return "medium";
  }
  return "low";
}

export function formatEvidence(evidence: string[]) {
  return evidence.map((item) => item.replace(/[=_]/g, " ").trim()).filter(Boolean);
}

export function formatTimeRange(startSec: number, endSec: number) {
  return `${formatTime(startSec)}-${formatTime(endSec)}`;
}

export function formatTime(seconds: number | null) {
  if (seconds === null || !Number.isFinite(seconds)) {
    return "Unknown";
  }
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remainder = Math.round(safe % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${remainder}`;
}

function centerY(value: number, height: number) {
  const amplitude = value * (height / 2 - 2);
  return height / 2 - amplitude;
}

function clampUnit(value: number) {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, Math.min(1, value));
}

function clampPercent(value: number) {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, Math.min(100, value));
}

function round(value: number) {
  return Math.round(value * 100) / 100;
}

function titleCase(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
