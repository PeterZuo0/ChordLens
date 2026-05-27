export type BeatLength = 1 | 2 | 4 | 8;
export type ChordName = "C" | "D" | "E" | "F" | "G" | "A" | "B";

export interface ChordLoopEvent {
  id: string;
  chord: ChordName;
  beats: BeatLength;
  createdAt: string;
}
