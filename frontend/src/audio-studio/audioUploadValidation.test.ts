import { describe, expect, it } from "vitest";

import { isAllowedAudioFileName } from "./audioUploadValidation";

describe("audioUploadValidation", () => {
  it("accepts supported local audio file names case-insensitively", () => {
    expect(isAllowedAudioFileName("track.MP3")).toBe(true);
    expect(isAllowedAudioFileName("loop.wav")).toBe(true);
    expect(isAllowedAudioFileName("idea.m4a")).toBe(true);
  });

  it("rejects unsupported or missing file extensions", () => {
    expect(isAllowedAudioFileName("notes.txt")).toBe(false);
    expect(isAllowedAudioFileName("audio")).toBe(false);
  });
});
