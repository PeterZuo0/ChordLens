import type { ReactNode } from "react";

import { routes } from "./routes";

interface StatusItem {
  label: string;
  tone?: "ok" | "warn" | "muted";
  value: string;
}

interface AppShellProps {
  activeRoute?: string;
  children: ReactNode;
  statusItems?: StatusItem[];
}

const navItems = [
  { href: routes.home, label: "Workspace" },
  { href: routes.audioStudio, label: "Audio Studio" },
  { href: routes.arLooper, label: "AR Looper" }
];

export function AppShell({ activeRoute, children, statusItems = [] }: AppShellProps) {
  return (
    <main className="app-shell console-shell">
      <aside className="side-nav" aria-label="Primary navigation">
        <a className="brand" href={routes.home}>
          ChordLens
        </a>
        <nav className="nav-links">
          {navItems.map((item) => (
            <a aria-current={activeRoute === item.href ? "page" : undefined} href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </nav>
        <div className="local-policy">
          <span>LOCAL-FIRST</span>
          <small>No accounts, cloud sync, or streaming extraction.</small>
        </div>
      </aside>
      <div className="console-main">
        {children}
        {statusItems.length ? (
          <footer className="status-strip" aria-label="Workspace status">
            {statusItems.map((item) => (
              <span className={item.tone ? `status-item ${item.tone}` : "status-item"} key={item.label}>
                <strong>{item.label}</strong>
                <span>{item.value}</span>
              </span>
            ))}
          </footer>
        ) : null}
      </div>
    </main>
  );
}
