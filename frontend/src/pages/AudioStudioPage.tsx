import { useState } from "react";

import { analyzeAudioFile } from "../api/client";
import type { TransientAudioAnalysisResponse } from "../api/types";
import { AnalysisSummary } from "../audio-studio/AnalysisSummary";
import { AudioUploadPanel } from "../audio-studio/AudioUploadPanel";
import { StemControls } from "../audio-studio/StemControls";
import { routes } from "../app/routes";

export function AudioStudioPage() {
  const [analysis, setAnalysis] = useState<TransientAudioAnalysisResponse | null>(null);

  async function handleAnalyze(file: File, separateStems: boolean) {
    const nextAnalysis = await analyzeAudioFile(file, separateStems);
    setAnalysis(nextAnalysis);
  }

  return (
    <main className="app-shell workbench">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href={routes.home}>
          ChordLens
        </a>
        <div className="nav-links">
          <a aria-current="page" href={routes.audioStudio}>
            Audio Studio
          </a>
          <a href={routes.arLooper}>AR Looper</a>
        </div>
      </nav>

      <header className="page-header">
        <div>
          <h1>Audio Analysis Studio</h1>
          <p>Upload local audio for one-time BPM, key, metadata, and optional stem analysis.</p>
        </div>
        <span className="phase-tag">Temporary best-effort analysis</span>
      </header>

      <div className="studio-layout">
        <AudioUploadPanel onAnalyze={handleAnalyze} />
        <AnalysisSummary analysis={analysis} />
        <StemControls stems={analysis?.stems ?? null} />
      </div>
    </main>
  );
}
