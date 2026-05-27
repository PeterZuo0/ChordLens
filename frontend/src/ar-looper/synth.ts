import type { ChordName } from "./types";

const majorTriads: Record<ChordName, number[]> = {
  C: [261.63, 329.63, 392],
  D: [293.66, 369.99, 440],
  E: [329.63, 415.3, 493.88],
  F: [349.23, 440, 523.25],
  G: [392, 493.88, 587.33],
  A: [440, 554.37, 659.25],
  B: [493.88, 622.25, 739.99]
};

let context: AudioContext | null = null;

function getAudioContext() {
  context ??= new AudioContext();
  return context;
}

export function playChordPreview(chord: ChordName) {
  const audio = getAudioContext();
  const now = audio.currentTime;
  const output = audio.createGain();
  output.gain.setValueAtTime(0.0001, now);
  output.gain.exponentialRampToValueAtTime(0.16, now + 0.03);
  output.gain.exponentialRampToValueAtTime(0.0001, now + 0.75);
  output.connect(audio.destination);

  majorTriads[chord].forEach((frequency) => {
    const oscillator = audio.createOscillator();
    oscillator.type = "triangle";
    oscillator.frequency.setValueAtTime(frequency, now);
    oscillator.connect(output);
    oscillator.start(now);
    oscillator.stop(now + 0.8);
  });
}
