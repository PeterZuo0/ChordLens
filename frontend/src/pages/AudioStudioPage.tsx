import { useState } from "react";

import { createAudioProject, getAudioProjectAnalysis, uploadAudioFile } from "../api/client";
import type { AnalysisSummary as AnalysisSummaryType, ProjectSummary } from "../api/types";
import { AnalysisSummary } from "../audio-studio/AnalysisSummary";
import { AudioUploadPanel } from "../audio-studio/AudioUploadPanel";
import { ChordTimeline } from "../audio-studio/ChordTimeline";
import { StemControls } from "../audio-studio/StemControls";
import { routes } from "../app/routes";

export function AudioStudioPage() {
  const [project, setProject] = useState<ProjectSummary | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisSummaryType | null>(null);

  async function loadAnalysis(nextProject: ProjectSummary) {
    setProject(nextProject);
    const nextAnalysis = await getAudioProjectAnalysis(nextProject.id);
    setAnalysis(nextAnalysis);
  }

  async function handleUpload(file: File) {
    const nextProject = await uploadAudioFile(file);
    await loadAnalysis(nextProject);
  }

  async function handleCreateMock() {
    const nextProject = await createAudioProject("Mock practice song");
    await loadAnalysis(nextProject);
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
          <p>Upload local audio and inspect a clearly labeled mock analysis workspace.</p>
        </div>
        <span className="phase-tag">Phase 2A mock analysis</span>
      </header>

      <div className="studio-layout">
        <AudioUploadPanel onCreateMock={handleCreateMock} onUpload={handleUpload} />
        <AnalysisSummary analysis={analysis} project={project} />
        <ChordTimeline chords={analysis?.chords ?? []} />
        <StemControls stems={analysis?.stems ?? []} />
      </div>
    </main>
  );
}
