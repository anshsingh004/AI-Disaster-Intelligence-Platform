import React from "react";
import "./EmptyState.css";

export default function EmptyState({
  icon = "radar",
  title = "No Active Incident Alerts",
  subtitle = "All operational sectors reporting normal telemetry.",
  actionLabel,
  onAction,
  compact = false,
  className = "",
}) {
  return (
    <div className={`empty-state-root${compact ? " empty-state-compact" : ""} ${className}`}>
      <div className="empty-state-icon-wrap">
        <span className="material-symbols-outlined empty-state-icon">{icon}</span>
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-subtitle">{subtitle}</p>
      {actionLabel && onAction && (
        <button className="btn-tonal empty-state-action" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
