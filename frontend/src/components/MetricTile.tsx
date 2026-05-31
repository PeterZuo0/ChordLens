import type { ReactNode } from "react";

interface MetricTileProps {
  detail?: ReactNode;
  label: string;
  tone?: "primary" | "accent" | "cool" | "muted";
  value: ReactNode;
}

export function MetricTile({ detail, label, tone = "muted", value }: MetricTileProps) {
  return (
    <div className={`metric-tile ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </div>
  );
}
