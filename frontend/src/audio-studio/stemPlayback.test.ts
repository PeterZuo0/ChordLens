import { describe, expect, it } from "vitest";

import type { TransientStemItem } from "../api/types";
import {
  buildStemTrackStates,
  getStemAudibleVolume,
  resolveApiAssetUrl,
  setStemVolume,
  toggleStemMute,
  toggleStemSolo
} from "./stemPlayback";

const items: TransientStemItem[] = ["vocals", "drums", "bass", "other", "piano", "strings"].map((name) => ({
  name: name as TransientStemItem["name"],
  status: "complete",
  format: "wav",
  mimeType: "audio/wav",
  fileSizeBytes: 1024,
  durationSec: null,
  streamUrl: `/api/audio/stem-sessions/session/stems/${name}`,
  downloadUrl: `/api/audio/stem-sessions/session/stems/${name}/download`,
  message: null,
  analysis: null
}));

describe("stemPlayback", () => {
  it("builds one playable track state for each returned stem item", () => {
    const tracks = buildStemTrackStates(items);

    expect(tracks).toHaveLength(6);
    expect(tracks.map((track) => track.name)).toEqual(["vocals", "drums", "bass", "other", "piano", "strings"]);
    expect(tracks.every((track) => track.volume === 1 && !track.muted && !track.soloed)).toBe(true);
  });

  it("mutes a stem without changing its stored volume", () => {
    const tracks = toggleStemMute(buildStemTrackStates(items), "vocals");

    expect(tracks.find((track) => track.name === "vocals")).toMatchObject({ muted: true, volume: 1 });
    expect(getStemAudibleVolume(tracks, "vocals")).toBe(0);
  });

  it("soloes selected stems and silences non-soloed stems", () => {
    const tracks = toggleStemSolo(buildStemTrackStates(items), "drums");

    expect(getStemAudibleVolume(tracks, "drums")).toBe(1);
    expect(getStemAudibleVolume(tracks, "vocals")).toBe(0);
  });

  it("clamps volume controls to the valid audio range", () => {
    const tracks = setStemVolume(buildStemTrackStates(items), "bass", 1.8);
    const nextTracks = setStemVolume(tracks, "other", -0.3);

    expect(nextTracks.find((track) => track.name === "bass")?.volume).toBe(1);
    expect(nextTracks.find((track) => track.name === "other")?.volume).toBe(0);
  });

  it("resolves relative backend asset URLs against the API origin", () => {
    expect(resolveApiAssetUrl("/api/audio/stem-sessions/session/stems/vocals", "http://127.0.0.1:8000")).toBe(
      "http://127.0.0.1:8000/api/audio/stem-sessions/session/stems/vocals"
    );
    expect(resolveApiAssetUrl("https://example.test/file.wav", "http://127.0.0.1:8000")).toBe(
      "https://example.test/file.wav"
    );
  });
});
