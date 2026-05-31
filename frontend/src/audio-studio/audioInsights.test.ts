import { describe, expect, it } from "vitest";

import {
  buildStructureSegments,
  confidenceTone,
  formatEvidence,
  getVisibleAndTechnicalHints,
  makeSpectrumBars,
  makeWaveformPath,
  sectionLabel
} from "./audioInsights";

describe("audioInsights", () => {
  it("normalizes structure sections into percent widths", () => {
    const segments = buildStructureSegments([
      { startSec: 0, endSec: 10, label: "intro", confidence: 0.5, reason: null },
      { startSec: 10, endSec: 30, label: "chorus", confidence: 0.7, reason: null }
    ]);

    expect(segments[0].left).toBe(0);
    expect(segments[0].width).toBeCloseTo(33.333, 1);
    expect(segments[1].width).toBeCloseTo(66.666, 1);
  });

  it("splits visible and technical instrument hints", () => {
    const result = getVisibleAndTechnicalHints([
      { label: "piano", confidence: 0.7, source: "other", evidence: [], visible: true },
      { label: "synth", confidence: 0.4, source: "full_mix", evidence: [], visible: false }
    ]);

    expect(result.visible[0].label).toBe("piano");
    expect(result.technical[0].label).toBe("synth");
  });

  it("builds stable svg geometry from real analysis arrays", () => {
    expect(makeWaveformPath([0, 0.5, 1], 120, 32)).toContain("M");
    expect(makeSpectrumBars([0, 0.5, 1], 120, 32)).toHaveLength(3);
  });

  it("does not fabricate waveform geometry when real arrays are empty", () => {
    expect(makeWaveformPath([], 120, 32)).toBe("");
    expect(makeSpectrumBars([], 120, 32)).toEqual([]);
  });

  it("formats section labels, confidence tones, and evidence", () => {
    expect(sectionLabel("pre_chorus")).toBe("Pre-chorus");
    expect(confidenceTone(0.72)).toBe("high");
    expect(confidenceTone(0.45)).toBe("medium");
    expect(confidenceTone(0.2)).toBe("low");
    expect(formatEvidence(["source=other", "rms=0.2"])).toEqual(["source other", "rms 0.2"]);
  });
});
