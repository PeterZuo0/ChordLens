import { useState } from "react";

interface AudioUploadPanelProps {
  onAnalyze: (file: File, separateStems: boolean) => Promise<void>;
}

const allowedExtensions = [".mp3", ".wav", ".m4a"];

export function AudioUploadPanel({ onAnalyze }: AudioUploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [separateStems, setSeparateStems] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    setError(null);
  }

  async function runAnalysis() {
    if (!file) {
      setError("Choose an mp3, wav, or m4a file first.");
      return;
    }

    const lowerName = file.name.toLowerCase();
    if (!allowedExtensions.some((extension) => lowerName.endsWith(extension))) {
      setError("Unsupported file type. Use mp3, wav, or m4a.");
      return;
    }

    setBusy(true);
    setError(null);
    try {
      await onAnalyze(file, separateStems);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Analysis failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="tool-panel upload-panel">
      <div className="panel-heading">
        <span className="panel-label">Audio Studio</span>
        <strong>Local upload</strong>
      </div>
      <label className="file-drop">
        <input accept=".mp3,.wav,.m4a" type="file" onChange={handleFileChange} />
        <span>{file ? file.name : "Choose an audio file"}</span>
        <small>mp3, wav, or m4a. Files are analyzed once and not saved.</small>
      </label>
      <label className="toggle-row">
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
      {error ? <p className="error-text">{error}</p> : null}
      <div className="button-row">
        <button className="button primary" disabled={busy} onClick={runAnalysis} type="button">
          {busy ? "Analyzing..." : "Analyze"}
        </button>
      </div>
    </section>
  );
}
