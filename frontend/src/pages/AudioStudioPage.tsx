import { useState } from "react";

import { analyzeAudioFile, clearStemSession } from "../api/client";
import type { TransientAudioAnalysisResponse } from "../api/types";
import { AnalysisSummary } from "../audio-studio/AnalysisSummary";
import { AudioUploadPanel } from "../audio-studio/AudioUploadPanel";
import { ChordHintTimeline } from "../audio-studio/ChordHintTimeline";
import { SongStructureTimeline } from "../audio-studio/SongStructureTimeline";
import { StemReviewConsole } from "../audio-studio/StemReviewConsole";
import { useWorkbenchMotion } from "../audio-studio/useWorkbenchMotion";
import { AppShell } from "../app/AppShell";
import { routes } from "../app/routes";

export function AudioStudioPage() {
  const [analysis, setAnalysis] = useState<TransientAudioAnalysisResponse | null>(null);
  const [lastFile, setLastFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const motionRootRef = useWorkbenchMotion(analysis?.source.fileName ?? null);
  const hasAnalysis = analysis !== null;
  const hasCompleteStems = analysis?.stems.status === "complete";

  async function handleAnalyze(file: File, separateStems: boolean) {
    setLastFile(file);
    setIsAnalyzing(true);
    try {
      const nextAnalysis = await analyzeAudioFile(file, separateStems);
      setAnalysis(nextAnalysis);
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function retryStemAnalysis() {
    if (!lastFile) {
      return;
    }
    await handleAnalyze(lastFile, true);
  }

  async function handleClearStemSession(sessionId: string) {
    await clearStemSession(sessionId);
    setAnalysis((current) =>
      current
        ? {
            ...current,
            stems: {
              requested: false,
              status: "not_requested",
              sessionId: null,
              engine: null,
              items: [],
              zipDownloadUrl: null,
              message: null
            }
          }
        : current
    );
  }

  function startNewAnalysis() {
    setAnalysis(null);
    setLastFile(null);
  }

  return (
    <AppShell
      activeRoute={routes.audioStudio}
      statusItems={[
        { label: "Endpoint", value: "POST /api/audio/analyze", tone: "muted" },
        { label: "Result", value: analysis ? "Temporary" : "None", tone: analysis ? "warn" : "muted" },
        { label: "Storage", value: "Page-local", tone: "ok" }
      ]}
    >
      <div className="audio-studio-flow" ref={motionRootRef}>
        <header className="workspace-header a1-motion-item">
          <div>
            <span className="panel-label">Audio Studio</span>
            <h1>Audio Analysis Studio</h1>
            <p>Upload local audio for one-time BPM, key, metadata, structure, waveform, and optional stem analysis.</p>
          </div>
          <span className="phase-tag">Temporary best-effort analysis</span>
        </header>

        <div
          className={[
            "audio-workbench",
            "a1-workbench",
            hasAnalysis ? "analysis-expanded" : "",
            hasCompleteStems ? "stems-expanded" : ""
          ]
            .filter(Boolean)
            .join(" ")}
        >
          <div className="a1-motion-item upload-workbench-cell">
            <AudioUploadPanel
              compact={hasAnalysis && !isAnalyzing}
              currentFileName={analysis?.source.fileName ?? null}
              onAnalyze={handleAnalyze}
              onNew={startNewAnalysis}
            />
          </div>
          <div className="a1-motion-item analysis-workbench-cell">
            <AnalysisSummary analysis={analysis} />
          </div>
          <div className={hasAnalysis ? "a1-motion-item stem-workbench-cell" : "a1-motion-item"}>
            <StemReviewConsole
              onClearSession={handleClearStemSession}
              onRetry={retryStemAnalysis}
              processing={isAnalyzing}
              stems={analysis?.stems ?? null}
            />
          </div>
        </div>

        <div className="analysis-timeline-grid">
          <SongStructureTimeline
            durationSec={analysis?.source.durationSec ?? null}
            sections={analysis?.music.structure ?? []}
          />
          <ChordHintTimeline hints={analysis?.music.chordHints ?? []} />
        </div>
      </div>
    </AppShell>
  );
}
