import { useEffect, useRef, useState } from "react";

import gsap from "gsap";

import { allowedAudioExtensions, isAllowedAudioFileName } from "./audioUploadValidation";
import { getLoadingProgress } from "./loadingProgress";

interface AudioUploadPanelProps {
  compact?: boolean;
  currentFileName?: string | null;
  onAnalyze: (file: File, separateStems: boolean) => Promise<void>;
  onNew?: () => void;
}

export function AudioUploadPanel({ compact = false, currentFileName = null, onAnalyze, onNew }: AudioUploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [separateStems, setSeparateStems] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const dropZoneRef = useRef<HTMLLabelElement | null>(null);

  const progress = getLoadingProgress(elapsedMs, separateStems);

  useEffect(() => {
    if (!busy) {
      return undefined;
    }

    const startedAt = Date.now();
    const intervalId = window.setInterval(() => {
      setElapsedMs(Date.now() - startedAt);
    }, 180);

    return () => window.clearInterval(intervalId);
  }, [busy]);

  useEffect(() => {
    if (!dropZoneRef.current) {
      return undefined;
    }

    const motion = gsap.matchMedia();
    motion.add(
      {
        reduce: "(prefers-reduced-motion: reduce)",
        animate: "(prefers-reduced-motion: no-preference)"
      },
      (context) => {
        if (context.conditions?.reduce) {
          return;
        }
        gsap.to(dropZoneRef.current, {
          borderColor: dragActive ? "rgba(79, 208, 138, 0.88)" : "rgba(86, 100, 91, 1)",
          duration: 0.2,
          ease: "power2.out",
          scale: dragActive ? 1.01 : 1,
          overwrite: "auto"
        });
      },
      dropZoneRef.current
    );

    return () => motion.revert();
  }, [dragActive]);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    chooseFile(selected);
  }

  function chooseFile(selected: File | null) {
    setDragActive(false);
    if (!selected) {
      return;
    }
    if (!isAllowedAudioFileName(selected.name)) {
      setError("Unsupported file type. Use mp3, wav, or m4a.");
      return;
    }
    setFile(selected);
    setError(null);
  }

  async function runAnalysis(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose an mp3, wav, or m4a file first.");
      return;
    }

    if (!isAllowedAudioFileName(file.name)) {
      setError("Unsupported file type. Use mp3, wav, or m4a.");
      return;
    }

    setBusy(true);
    setElapsedMs(0);
    setError(null);
    try {
      await onAnalyze(file, separateStems);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Analysis failed.");
    } finally {
      setBusy(false);
    }
  }

  function handleDragOver(event: React.DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    if (!busy) {
      event.dataTransfer.dropEffect = "copy";
      setDragActive(true);
    }
  }

  function handleDragLeave(event: React.DragEvent<HTMLLabelElement>) {
    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
      setDragActive(false);
    }
  }

  function handleDrop(event: React.DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    if (busy) {
      setDragActive(false);
      return;
    }
    chooseFile(event.dataTransfer.files?.[0] ?? null);
  }

  if (compact && !busy) {
    return (
      <section className="tool-panel upload-panel compact-upload-panel" aria-label="Current audio source">
        <span className="panel-label">Loaded</span>
        {currentFileName ? <strong title={currentFileName}>{currentFileName}</strong> : null}
        <button className="button primary new-upload-button" onClick={onNew} type="button">
          New
        </button>
      </section>
    );
  }

  return (
    <form className="tool-panel upload-panel source-panel enlarged-upload-panel" onSubmit={runAnalysis}>
      <div className="panel-heading">
        <span className="panel-label">Audio Studio</span>
        <strong>Local upload</strong>
      </div>
      <input
        accept={allowedAudioExtensions.join(",")}
        className="file-input"
        disabled={busy}
        id="audio-upload-input"
        type="file"
        onChange={handleFileChange}
      />
      <label
        className={dragActive ? "file-drop console-drop drag-active" : "file-drop console-drop"}
        htmlFor="audio-upload-input"
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        ref={dropZoneRef}
      >
        <span className="drop-zone-kicker">{dragActive ? "Drop to load" : "Drag audio here"}</span>
        <span className="file-name">{file ? file.name : "Choose an audio file"}</span>
        <small>Drop or browse an mp3, wav, or m4a. Files are analyzed once and not saved.</small>
      </label>
      <label className="toggle-row console-toggle">
        <input
          checked={separateStems}
          disabled={busy}
          onChange={(event) => setSeparateStems(event.target.checked)}
          type="checkbox"
        />
        <span>
          <strong>Separate stems</strong>
          <small>Optional and slower. Stem files stay temporary and only a status summary is returned.</small>
        </span>
      </label>
      {busy ? (
        <div className="analysis-progress compact" role="status" aria-live="polite">
          <div className="analysis-progress-meta">
            <strong>{progress.label}</strong>
            <span>{progress.percent}%</span>
          </div>
          <div
            aria-label="Audio analysis progress"
            aria-valuemax={100}
            aria-valuemin={0}
            aria-valuenow={progress.percent}
            className="analysis-progress-track"
            role="progressbar"
          >
            <span style={{ width: `${progress.percent}%` }} />
          </div>
          <small>{progress.detail}</small>
        </div>
      ) : null}
      {error ? <p className="error-text">{error}</p> : null}
      <div className="button-row">
        <button className="button primary" disabled={busy} type="submit">
          {busy ? "Analyzing..." : "Analyze"}
        </button>
      </div>
    </form>
  );
}
