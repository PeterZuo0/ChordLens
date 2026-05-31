import { describe, expect, it } from "vitest";

import { getLoadingProgress } from "./loadingProgress";

describe("getLoadingProgress", () => {
  it("returns staged progress for normal audio analysis", () => {
    expect(getLoadingProgress(0, false)).toMatchObject({
      percent: 12,
      label: "Preparing audio"
    });
    expect(getLoadingProgress(1800, false)).toMatchObject({
      label: "Reading metadata"
    });
    expect(getLoadingProgress(4200, false)).toMatchObject({
      label: "Estimating BPM and key"
    });
  });

  it("adds a stem separation stage only when requested", () => {
    expect(getLoadingProgress(7600, false).label).toBe("Estimating BPM and key");
    expect(getLoadingProgress(7600, true).label).toBe("Checking stem separation");
  });

  it("caps best-effort progress before completion", () => {
    expect(getLoadingProgress(60000, false).percent).toBe(90);
    expect(getLoadingProgress(60000, true).percent).toBe(90);
  });
});
