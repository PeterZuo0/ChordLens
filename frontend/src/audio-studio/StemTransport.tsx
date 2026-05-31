interface StemTransportProps {
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  onPause: () => void;
  onPlay: () => void;
  onSeek: (timeSec: number) => void;
}

export function StemTransport({ currentTime, duration, isPlaying, onPause, onPlay, onSeek }: StemTransportProps) {
  return (
    <div className="stem-transport">
      <button className="transport-play" onClick={isPlaying ? onPause : onPlay} type="button">
        {isPlaying ? "Pause" : "Play"}
      </button>
      <div className="stem-time">
        <strong>{formatTime(currentTime)}</strong>
        <span>{formatTime(duration)}</span>
      </div>
      <input
        aria-label="Stem playback position"
        className="stem-seek"
        max={duration || 0}
        min="0"
        onChange={(event) => onSeek(Number(event.target.value))}
        step="0.05"
        type="range"
        value={Math.min(currentTime, duration || currentTime)}
      />
    </div>
  );
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds <= 0) {
    return "0:00";
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${remainingSeconds}`;
}
