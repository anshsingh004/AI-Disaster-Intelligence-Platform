import React from "react";
import "./BackendPending.css";

export default function BackendPending({ onNavigate }) {
  return (
    <div className="bp-root fade-in">
      <div className="bp-card card-lift">
        <div className="bp-icon-wrap">
          <div className="bp-icon-ring">
            <span className="material-symbols-outlined bp-icon">construction</span>
          </div>
          <div className="bp-pulse-ring" />
          <div className="bp-pulse-ring bp-pulse-ring-2" />
        </div>

        <div className="bp-content">
          <div className="bp-chip">
            <span className="material-symbols-outlined" style={{fontSize:14}}>schedule</span>
            Backend Configuration Pending
          </div>
          <h1 className="bp-title">The Backend Is Yet to Be Configured</h1>
          <p className="bp-desc">
            This feature is part of the Terra-Aura Intelligence platform and is currently in development.
            The backend services — including API endpoints, database connections, and AI inference pipelines —
            will be fully configured in the next phase of deployment.
          </p>

          <div className="bp-status-grid">
            {[
              { label: "API Endpoints",    status: "pending",    icon: "api" },
              { label: "Database",         status: "pending",    icon: "storage" },
              { label: "AI Models",        status: "pending",    icon: "psychology" },
              { label: "Auth Services",    status: "pending",    icon: "lock" },
              { label: "Frontend Design",  status: "complete",   icon: "web" },
              { label: "Routing",          status: "complete",   icon: "route" },
            ].map((item) => (
              <div key={item.label} className={`bp-status-item bp-status-${item.status}`}>
                <span className="material-symbols-outlined bp-status-icon">{item.icon}</span>
                <div>
                  <p className="bp-status-label">{item.label}</p>
                  <span className={`badge badge-${item.status === "complete" ? "resolved" : "monitoring"}`}>
                    {item.status === "complete" ? "Complete" : "Pending"}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="bp-actions">
            <button
              id="btn-back-dashboard"
              className="btn-primary"
              onClick={() => onNavigate("disaster-center")}
            >
              <span className="material-symbols-outlined">arrow_back</span>
              Return to Disaster Center
            </button>
            <button
              id="btn-back-analytics"
              className="btn-outline"
              onClick={() => onNavigate("analytics")}
            >
              <span className="material-symbols-outlined">bar_chart</span>
              View Analytics
            </button>
          </div>
        </div>

        <div className="bp-footer">
          <span className="material-symbols-outlined" style={{fontSize:14, color:"var(--tertiary)"}}>info</span>
          <span>Terra-Aura Intelligence © 2024 — All backend features follow the same color theme and design system.</span>
        </div>
      </div>
    </div>
  );
}
