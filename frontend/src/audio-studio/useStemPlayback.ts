import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { StemName, TransientStemItem } from "../api/types";
import {
  buildStemTrackStates,
  getStemAudibleVolume,
  setStemVolume,
  type StemTrackState,
  toggleStemMute,
  toggleStemSolo
} from "./stemPlayback";

export function useStemPlayback(items: TransientStemItem[]) {
  const [tracks, setTracks] = useState<StemTrackState[]>(() => buildStemTrackStates(items));
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackError, setPlaybackError] = useState<string | null>(null);
  const audioRefs = useRef<Partial<Record<StemName, HTMLAudioElement>>>({});

  const sessionKey = useMemo(() => items.map((item) => `${item.name}:${item.streamUrl ?? ""}`).join("|"), [items]);

  useEffect(() => {
    setTracks(buildStemTrackStates(items));
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    setPlaybackError(null);
  }, [sessionKey]);

  useEffect(() => {
    for (const track of tracks) {
      const audio = audioRefs.current[track.name];
      if (audio) {
        audio.volume = getStemAudibleVolume(tracks, track.name);
      }
    }
  }, [tracks]);

  const registerAudio = useCallback((name: StemName, node: HTMLAudioElement | null) => {
    if (node) {
      audioRefs.current[name] = node;
    } else {
      delete audioRefs.current[name];
    }
  }, []);

  const play = useCallback(async () => {
    setPlaybackError(null);
    try {
      await Promise.all(
        Object.values(audioRefs.current)
          .filter((audio): audio is HTMLAudioElement => Boolean(audio))
          .map((audio) => audio.play())
      );
      setIsPlaying(true);
    } catch {
      setIsPlaying(false);
      setPlaybackError("Playback could not start. Check that the stem files are still available.");
    }
  }, []);

  const pause = useCallback(() => {
    for (const audio of Object.values(audioRefs.current)) {
      audio?.pause();
    }
    setIsPlaying(false);
  }, []);

  const unload = useCallback(() => {
    for (const audio of Object.values(audioRefs.current)) {
      if (audio) {
        try {
          audio.pause();
          audio.removeAttribute("src");
        } catch {
          // Media cleanup is best-effort; clearing the server session should still proceed.
        }
      }
    }
    setIsPlaying(false);
    setCurrentTime(0);
  }, []);

  const seek = useCallback((nextTime: number) => {
    const safeTime = Math.max(0, Math.min(duration || nextTime, nextTime));
    for (const audio of Object.values(audioRefs.current)) {
      if (audio) {
        audio.currentTime = safeTime;
      }
    }
    setCurrentTime(safeTime);
  }, [duration]);

  const syncMediaState = useCallback(() => {
    const audios = Object.values(audioRefs.current).filter((audio): audio is HTMLAudioElement => Boolean(audio));
    const nextDuration = Math.max(0, ...audios.map((audio) => (Number.isFinite(audio.duration) ? audio.duration : 0)));
    const nextTime = Math.max(0, ...audios.map((audio) => audio.currentTime || 0));
    setDuration(nextDuration);
    setCurrentTime(nextTime);
    if (nextDuration > 0 && nextTime >= nextDuration - 0.15) {
      setIsPlaying(false);
    }
  }, []);

  return {
    tracks,
    isPlaying,
    currentTime,
    duration,
    playbackError,
    registerAudio,
    play,
    pause,
    unload,
    seek,
    syncMediaState,
    toggleMute: (name: StemName) => setTracks((current) => toggleStemMute(current, name)),
    toggleSolo: (name: StemName) => setTracks((current) => toggleStemSolo(current, name)),
    setVolume: (name: StemName, volume: number) => setTracks((current) => setStemVolume(current, name, volume))
  };
}
