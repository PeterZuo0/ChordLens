import { routes } from "../app/routes";

export function NotFoundPage() {
  return (
    <main className="app-shell compact-page">
      <section className="tool-panel">
        <h1>Page not found</h1>
        <p>This local route is not part of the ChordLens skeleton.</p>
        <a className="button primary" href={routes.home}>
          Go home
        </a>
      </section>
    </main>
  );
}
