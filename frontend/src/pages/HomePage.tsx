import { useEffect, useState } from "react";

import { getHealth } from "../api/client";
import type { HealthResponse } from "../api/types";
import { AppShell } from "../app/AppShell";
import { routes } from "../app/routes";

export function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((response) => {
        setHealth(response);
        setError(null);
      })
      .catch((issue: Error) => {
        setHealth(null);
        setError(issue.message);
      });
  }, []);

  const backendStatus = health ? "Active" : error ? "Unavailable" : "Checking";

  return (
    <AppShell
      activeRoute={routes.home}
      statusItems={[
        { label: "Backend", value: backendStatus, tone: health ? "ok" : error ? "warn" : "muted" },
        { label: "Policy", value: "Local-only", tone: "ok" },
        { label: "Analysis", value: "Best-effort", tone: "muted" }
      ]}
    >
      <header className="workspace-header">
        <div>
          <span className="panel-label">Workspace</span>
          <h1>Local music analysis and chord-loop sketching.</h1>
          <p>
            Choose a focused local workflow. Audio results are temporary; AR hand tracking remains a
            planned adapter.
          </p>
        </div>
      </header>

      <section className="mode-grid" aria-label="ChordLens modes">
        <article className="mode-card featured">
          <span className="panel-label">Audio first</span>
          <h2>Audio Analysis Studio</h2>
          <p>
            Upload mp3, wav, or m4a files for temporary best-effort metadata, BPM, key, and optional
            local stem status.
          </p>
          <dl className="mode-facts">
            <div>
              <dt>Input</dt>
              <dd>mp3 / wav / m4a</dd>
            </div>
            <div>
              <dt>Result</dt>
              <dd>Page-local</dd>
            </div>
          </dl>
          <a className="button primary" href={routes.audioStudio}>
            Open Audio Studio
          </a>
        </article>

        <article className="mode-card">
          <span className="panel-label">Manual loop</span>
          <h2>AR Chord Looper</h2>
          <p>
            Commit chord events manually now with synth preview and a real loop timeline, preserving
            the future two-hand hover boundary.
          </p>
          <dl className="mode-facts">
            <div>
              <dt>Beats</dt>
              <dd>1 / 2 / 4 / 8</dd>
            </div>
            <div>
              <dt>Chords</dt>
              <dd>C-D-E-F-G-A-B</dd>
            </div>
          </dl>
          <a className="button secondary" href={routes.arLooper}>
            Open AR Looper
          </a>
        </article>
      </section>

      <section className="status-panel workspace-status" aria-live="polite">
        <span className="panel-label">Local backend</span>
        {health ? (
          <>
            <strong>Connected</strong>
            <span>
              {health.app} API {health.version}
            </span>
          </>
        ) : error ? (
          <>
            <strong>Unavailable</strong>
            <span>Start FastAPI on http://127.0.0.1:8000. {error}</span>
          </>
        ) : (
          <>
            <strong>Checking...</strong>
            <span>Looking for the local FastAPI server.</span>
          </>
        )}
      </section>
    </AppShell>
  );
}
