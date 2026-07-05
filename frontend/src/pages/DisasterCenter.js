import React, { useState } from "react";
import "./DisasterCenter.css";

const ALERTS = [
  {
    id: 1,
    level: "critical",
    title: "Unidentified Thermal Signature, Sector 4",
    time: "2 mins ago",
    desc: "Predictive models indicate a 94% probability of rapid expansion. Current atmospheric conditions heavily favor escalation. Immediate drone reconnaissance recommended.",
    prob: 87,
    contextData: [
      { icon: "air", title: "Wind Shear Anomaly", desc: "Local wind patterns have shifted 45° in the last hour, accelerating surface-level spread velocity." },
      { icon: "water_drop", title: "Moisture Index Drop", desc: "Vegetation moisture levels in immediate vicinity are below 12%, categorizing fuel state as critically volatile." },
    ],
  },
  {
    id: 2,
    level: "high",
    title: "Flood Risk Escalation, River Delta B7",
    time: "18 mins ago",
    desc: "Sustained rainfall upstream combined with compromised levee infrastructure creates high-probability inundation scenario in Delta B7 within 6 hours.",
    prob: 72,
    contextData: [
      { icon: "water_drop", title: "Rainfall Accumulation", desc: "24-hour totals exceeded 180mm across the watershed basin." },
      { icon: "terrain", title: "Levee Status", desc: "Section B7-C shows structural stress indicators above threshold." },
    ],
  },
];

export default function DisasterCenter({ user, onNavigate }) {
  const [activeAlert, setActiveAlert] = useState(ALERTS[0]);
  const [aiOpen, setAiOpen] = useState(true);
  const [acknowledged, setAcknowledged] = useState([]);

  const handleAck = (id) => setAcknowledged(prev => [...prev, id]);

  return (
    <div className="dc-root fade-in">
      {/* Top bar */}
      <header className="dc-topbar">
        <div className="dc-topbar-left">
          <div className="dc-live-badge">
            <span className="pulse-dot" />
            <span>Live Sync Active</span>
          </div>
          <span className="dc-sector-label">
            <span className="material-symbols-outlined" style={{fontSize:16}}>location_on</span>
            Sector Alpha — Thermal anomaly detected
          </span>
        </div>
        <div className="dc-topbar-right">
          <button id="btn-new-incident" className="btn-primary" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">add_circle</span>
            New Incident
          </button>
          <button id="btn-satellite" className="btn-tonal" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">satellite_alt</span>
            Satellite Overlay
          </button>
          <button id="btn-broadcast" className="btn-tonal" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">warning</span>
            Broadcast Alert
          </button>
          <button className="btn-icon" aria-label="Search" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">search</span>
          </button>
          <button className="btn-icon" aria-label="Notifications" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">notifications</span>
          </button>
        </div>
      </header>

      <div className="dc-body">
        {/* Map area */}
        <div className="dc-map-panel">
          <div className="dc-map-bg" />
          <div className="dc-map-controls">
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="Fullscreen">
              <span className="material-symbols-outlined">fullscreen</span>
            </button>
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="Zoom in">
              <span className="material-symbols-outlined">add</span>
            </button>
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="Zoom out">
              <span className="material-symbols-outlined">remove</span>
            </button>
            <button className="btn-icon dc-map-btn" onClick={() => onNavigate("backend-pending")} aria-label="My location">
              <span className="material-symbols-outlined">my_location</span>
            </button>
          </div>

          {/* Alert pins */}
          {ALERTS.map((a, i) => (
            <div
              key={a.id}
              className={`dc-map-pin dc-map-pin-${a.level}${activeAlert.id === a.id ? " dc-map-pin-active" : ""}`}
              style={{ top: `${30 + i * 25}%`, left: `${25 + i * 20}%` }}
              onClick={() => setActiveAlert(a)}
              aria-label={a.title}
            >
              <span className="material-symbols-outlined">warning</span>
            </div>
          ))}

          <div className="dc-map-label">Disaster Center — Global Monitoring</div>
        </div>

        {/* AI Analysis sidebar */}
        <div className={`dc-ai-panel${aiOpen ? "" : " dc-ai-collapsed"}`}>
          <div className="dc-ai-header" onClick={() => setAiOpen(!aiOpen)}>
            <div className="dc-ai-title-row">
              <span className="material-symbols-outlined dc-ai-icon">psychology</span>
              <span className="dc-ai-title">AI Analysis</span>
              <span className="dc-ai-live-chip">
                <span className="pulse-dot pulse-red" />
                Live
              </span>
            </div>
            <span className="material-symbols-outlined dc-ai-chevron">{aiOpen ? "expand_more" : "chevron_right"}</span>
          </div>

          {aiOpen && (
            <div className="dc-ai-body slide-in">
              {/* Alert selector */}
              <div className="dc-alert-tabs">
                {ALERTS.map(a => (
                  <button
                    key={a.id}
                    className={`dc-alert-tab${activeAlert.id === a.id ? " active" : ""} dc-alert-tab-${a.level}`}
                    onClick={() => setActiveAlert(a)}
                  >
                    <span className="material-symbols-outlined" style={{fontSize:14}}>warning</span>
                    <span className={`badge badge-${a.level}`}>{a.level.charAt(0).toUpperCase() + a.level.slice(1)}</span>
                    <span className="dc-alert-tab-time">{a.time}</span>
                  </button>
                ))}
              </div>

              <div className="dc-alert-card">
                <div className="dc-alert-card-header">
                  <span className={`badge badge-${activeAlert.level}`}>
                    <span className="material-symbols-outlined" style={{fontSize:11}}>warning</span>
                    {activeAlert.level.charAt(0).toUpperCase() + activeAlert.level.slice(1)} Alert
                  </span>
                  <span className="dc-alert-time">{activeAlert.time}</span>
                </div>
                <h3 className="dc-alert-title">{activeAlert.title}</h3>
                <p className="dc-alert-desc">{activeAlert.desc}</p>

                <div className="dc-alert-actions">
                  <button
                    id={`btn-view-details-${activeAlert.id}`}
                    className="btn-primary"
                    style={{flex:1}}
                    onClick={() => onNavigate("reports")}
                  >
                    View Details
                  </button>
                  <button
                    id={`btn-acknowledge-${activeAlert.id}`}
                    className={`btn-outline${acknowledged.includes(activeAlert.id) ? " acknowledged" : ""}`}
                    style={{flex:1}}
                    onClick={() => handleAck(activeAlert.id)}
                    disabled={acknowledged.includes(activeAlert.id)}
                  >
                    {acknowledged.includes(activeAlert.id) ? "✓ Acknowledged" : "Acknowledge"}
                  </button>
                </div>

                <div className="dc-context-section">
                  <p className="dc-context-label">Contextual Data</p>
                  {activeAlert.contextData.map((ctx, i) => (
                    <div key={i} className="dc-context-item">
                      <div className="dc-context-icon-wrap">
                        <span className="material-symbols-outlined">{ctx.icon}</span>
                      </div>
                      <div>
                        <p className="dc-context-title">{ctx.title}</p>
                        <p className="dc-context-desc">{ctx.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="dc-prob-section">
                  <div className="dc-prob-header">
                    <span className="dc-prob-label">Escalation Probability</span>
                    <span className="dc-prob-value" style={{color: activeAlert.prob > 80 ? "var(--error)" : "var(--secondary)"}}>{activeAlert.prob}%</span>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${activeAlert.prob}%`,
                        background: activeAlert.prob > 80 ? "var(--error)" : "var(--primary)"
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
