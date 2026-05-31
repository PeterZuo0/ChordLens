import { describe, expect, it } from "vitest";

import { formatConfidence, getPrimaryTempoLabel, sortInstrumentHints } from "./analysisFormatting";

describe("analysisFormatting", () => {
  it("formats missing confidence as unknown", () => {
    expect(formatConfidence(null)).toBe("Unknown");
  });

  it("uses bpm candidates when primary bpm is missing", () => {
    expect(
      getPrimaryTempoLabel({
        bpm: null,
        bpmCandidates: [{ bpm: 90, confidence: 0.5, source: "test", rawBpm: null }]
      })
    ).toBe("90 BPM");
  });

  it("sorts instrument hints by confidence descending", () => {
    const sorted = sortInstrumentHints([
      { label: "piano", confidence: 0.4 },
      { label: "strings", confidence: 0.8 }
    ]);

    expect(sorted[0].label).toBe("strings");
  });
});
