import { useState } from "react";

interface AudioUploadPanelProps {
  onUpload: (file: File) => Promise<void>;
  onCreateMock: () => Promise<void>;
}

const allowedExtensions = [".mp3", ".wav", ".m4a"];

export function AudioUploadPanel({ onUpload, onCreateMock }: AudioUploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    setError(null);
  }

  async function runUpload() {
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
      await onUpload(file);
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function createMock() {
    setBusy(true);
    setError(null);
    try {
      await onCreateMock();
    } catch (issue) {
      setError(issue instanceof Error ? issue.message : "Could not create mock project.");
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
        <small>mp3, wav, or m4a. Phase 2 stores the file and returns mock analysis.</small>
      </label>
      {error ? <p className="error-text">{error}</p> : null}
      <div className="button-row">
        <button className="button primary" disabled={busy} onClick={runUpload} type="button">
          {busy ? "Working..." : "Upload"}
        </button>
        <button className="button secondary" disabled={busy} onClick={createMock} type="button">
          Create mock project
        </button>
      </div>
    </section>
  );
}
