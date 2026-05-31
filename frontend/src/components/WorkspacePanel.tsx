import type { ReactNode } from "react";

interface WorkspacePanelProps {
  children: ReactNode;
  className?: string;
  label: string;
  meta?: ReactNode;
  title: ReactNode;
}

export function WorkspacePanel({ children, className, label, meta, title }: WorkspacePanelProps) {
  return (
    <section className={className ? `tool-panel ${className}` : "tool-panel"}>
      <div className="panel-heading">
        <span className="panel-label">{label}</span>
        <strong>{title}</strong>
        {meta ? <span className="panel-meta">{meta}</span> : null}
      </div>
      {children}
    </section>
  );
}
