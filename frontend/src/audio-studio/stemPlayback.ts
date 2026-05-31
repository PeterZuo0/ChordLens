import type { StemName, TransientStemItem } from "../api/types";

export interface StemTrackState {
  item: TransientStemItem;
  name: StemName;
  muted: boolean;
  soloed: boolean;
  volume: number;
}

export function buildStemTrackStates(items: TransientStemItem[]): StemTrackState[] {
  return items.map((item) => ({
    item,
    name: item.name,
    muted: false,
    soloed: false,
    volume: 1
  }));
}

export function toggleStemMute(tracks: StemTrackState[], name: StemName): StemTrackState[] {
  return tracks.map((track) => (track.name === name ? { ...track, muted: !track.muted } : track));
}

export function toggleStemSolo(tracks: StemTrackState[], name: StemName): StemTrackState[] {
  return tracks.map((track) => (track.name === name ? { ...track, soloed: !track.soloed } : track));
}

export function setStemVolume(tracks: StemTrackState[], name: StemName, volume: number): StemTrackState[] {
  const clamped = clampVolume(volume);
  return tracks.map((track) => (track.name === name ? { ...track, volume: clamped } : track));
}

export function getStemAudibleVolume(tracks: StemTrackState[], name: StemName): number {
  const track = tracks.find((candidate) => candidate.name === name);
  if (!track || track.muted) {
    return 0;
  }

  const hasSoloedTrack = tracks.some((candidate) => candidate.soloed);
  if (hasSoloedTrack && !track.soloed) {
    return 0;
  }

  return track.volume;
}

export function resolveApiAssetUrl(path: string, apiBaseUrl: string): string {
  try {
    return new URL(path).toString();
  } catch {
    return new URL(path, apiBaseUrl).toString();
  }
}

function clampVolume(volume: number): number {
  if (!Number.isFinite(volume)) {
    return 1;
  }
  return Math.max(0, Math.min(1, volume));
}
