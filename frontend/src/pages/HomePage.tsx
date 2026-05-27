import { useEffect, useState } from "react";

import { getHealth } from "../api/client";
import type { HealthResponse } from "../api/types";
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

  return (
    <main className="app-shell">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href={routes.home}>
          ChordLens
        </a>
        <div className="nav-links">
          <a href={routes.audioStudio}>Audio Studio</a>
          <a href={routes.arLooper}>AR Looper</a>
        </div>
      </nav>

      <section className="hero-panel">
        <div>
          <h1>Local music analysis and chord-loop sketching.</h1>
          <p>
            ChordLens starts as a local-first workspace for uploaded-song practice and fast chord loop
            experiments. Heavy analysis and camera tracking stay behind clear local interfaces.
          </p>
          <div className="hero-actions">
            <a className="button primary" href={routes.audioStudio}>
              Open Audio Studio
            </a>
            <a className="button secondary" href={routes.arLooper}>
              Open AR Looper
            </a>
          </div>
        </div>
        <div className="status-panel">
          <span className="panel-label">Backend</span>
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
        </div>
      </section>

      <section className="mode-grid" aria-label="ChordLens modes">
        <article className="mode-card">
          <span className="panel-label">Audio first</span>
          <h2>Audio Analysis Studio</h2>
          <p>Upload local audio, create a project, and inspect clearly labeled mock analysis output.</p>
          <a className="text-link" href={routes.audioStudio}>
            Continue
          </a>
        </article>
        <article className="mode-card">
          <span className="panel-label">Manual loop</span>
          <h2>AR Chord Looper</h2>
          <p>Build chord events manually now, with a future hand-tracking adapter boundary preserved.</p>
          <a className="text-link" href={routes.arLooper}>
            Continue
          </a>
        </article>
      </section>
    </main>
  );
}
