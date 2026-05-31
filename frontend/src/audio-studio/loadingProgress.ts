interface LoadingProgress {
  percent: number;
  label: string;
  detail: string;
}

export function getLoadingProgress(elapsedMs: number, separateStems: boolean): LoadingProgress {
  const safeElapsed = Math.max(0, elapsedMs);
  const percent = Math.min(90, 12 + Math.floor(safeElapsed / 220));

  if (separateStems && safeElapsed >= 7000) {
    return {
      percent,
      label: "Checking stem separation",
      detail: "Demucs availability and stem summary are checked only for this request."
    };
  }

  if (safeElapsed >= 3200) {
    return {
      percent,
      label: "Estimating BPM and key",
      detail: "Best-effort musical analysis is running locally."
    };
  }

  if (safeElapsed >= 1200) {
    return {
      percent,
      label: "Reading metadata",
      detail: "Duration, sample rate, channels, and format are being inspected."
    };
  }

  return {
    percent,
    label: "Preparing audio",
    detail: "The file is being prepared in temporary request storage."
  };
}
