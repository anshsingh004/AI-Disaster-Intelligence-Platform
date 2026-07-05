import React from "react";
import "./Dashboard.css";

const ACTIVE_INCIDENTS = [
  { id: 1, type: "Wildfire", sector: "Sector 7G", severity: 94, level: "critical", icon: "local_fire_department" },
  { id: 2, type: "Flood Warning", sector: "River Delta B7", severity: 72, level: "high", icon: "water_drop" },
  { id: 3, type: "Seismic Activity", sector: "Fault Line B", severity: 51, level: "medium", icon: "landscape" },
  { id: 4, type: "Cyclone Track", sector: "Bay of Bengal", severity: 88, level: "critical", icon: "cyclone" },
];

const QUICK_STATS = [
  { label: "Active Incidents", value: "124", icon: "warning", color: "var(--primary)", delta: "+3 today" },
  { label: "AI Confidence", value: "94%", icon: "psychology", color: "var(--secondary)", delta: "+5% this week" },
  { label: "Sectors Monitored", value: "47", icon: "radar", color: "var(--tertiary)", delta: "Global coverage" },
  { label: "Response Rate", value: "92%", icon: "speed", color: "#16a34a", delta: "+2% efficiency" },
];

export default function Dashboard({ user, onNavigate }) {
  return (
    <div className="dash-root fade-in">
      {/* Welcome banner */}
      <div className="dash-welcome">
        <div className="dash-welcome-text">
          <p className="dash-welcome-greeting">Good day, {user?.name?.split(" ")[0] || "Analyst"}</p>
          <h1 className="dash-welcome-title">Operations Dashboard</h1>
          <p className="dash-welcome-sub">
            Global monitoring active · {new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
          </p>
        </div>
        <div className="dash-welcome-live">
          <div className="dash-live-indicator">
            <span className="pulse-dot" />
            <span>Live Sync Active</span>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="dash-stats-grid">
        {QUICK_STATS.map((stat) => (
          <button
            key={stat.label}
            className="dash-stat-card card-lift"
            onClick={() => onNavigate("analytics")}
            id={`btn-stat-${stat.label.replace(/ /g, "-").toLowerCase()}`}
          >
            <div className="dash-stat-icon-wrap" style={{ background: `${stat.color}18` }}>
              <span className="material-symbols-outlined" style={{ color: stat.color }}>{stat.icon}</span>
            </div>
            <div className="dash-stat-info">
              <p className="dash-stat-value" style={{ color: stat.color }}>{stat.value}</p>
              <p className="dash-stat-label">{stat.label}</p>
              <p className="dash-stat-delta">{stat.delta}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Main content */}
      <div className="dash-main-grid">
        {/* Active incidents */}
        <div className="dash-incidents card-lift">
          <div className="dash-section-header">
            <h2 className="dash-section-title">Active Incidents</h2>
            <button className="btn-tonal" id="btn-view-all-incidents" onClick={() => onNavigate("reports")}>
              <span className="material-symbols-outlined">description</span>
              View All
            </button>
          </div>
          <div className="dash-incident-list">
            {ACTIVE_INCIDENTS.map((inc) => (
              <div
                key={inc.id}
                className="dash-incident-row"
                onClick={() => onNavigate("disaster-center")}
                role="button"
                tabIndex={0}
              >
                <div className={`dash-incident-icon dash-incident-icon-${inc.level}`}>
                  <span className="material-symbols-outlined">{inc.icon}</span>
                </div>
                <div className="dash-incident-info">
                  <p className="dash-incident-type">{inc.type}</p>
                  <p className="dash-incident-sector">{inc.sector}</p>
                </div>
                <div className="dash-incident-right">
                  <span className={`badge badge-${inc.level}`}>
                    {inc.level.charAt(0).toUpperCase() + inc.level.slice(1)}
                  </span>
                  <div className="dash-severity-bar">
                    <div
                      className="dash-severity-fill"
                      style={{
                        width: `${inc.severity}%`,
                        background: inc.level === "critical" ? "var(--error)" :
                                    inc.level === "high" ? "var(--primary)" : "var(--secondary)"
                      }}
                    />
                  </div>
                  <span className="dash-severity-val">{inc.severity}%</span>
                </div>
                <span className="material-symbols-outlined dash-incident-chevron">chevron_right</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick actions panel */}
        <div className="dash-actions-col">
          <div className="dash-quick-actions card-lift">
            <h2 className="dash-section-title">Quick Actions</h2>
            <div className="dash-action-grid">
              {[
                { label: "Disaster Center", icon: "map", page: "disaster-center", accent: "primary" },
                { label: "Run Analytics", icon: "bar_chart", page: "analytics", accent: "secondary" },
                { label: "Generate Report", icon: "description", page: "reports", accent: "tertiary" },
                { label: "New Incident", icon: "add_circle", page: "backend-pending", accent: "primary" },
                { label: "Broadcast Alert", icon: "warning", page: "backend-pending", accent: "error" },
                { label: "Satellite View", icon: "satellite_alt", page: "backend-pending", accent: "tertiary" },
              ].map((action) => (
                <button
                  key={action.label}
                  id={`btn-quick-${action.label.replace(/ /g, "-").toLowerCase()}`}
                  className="dash-action-btn"
                  onClick={() => onNavigate(action.page)}
                  style={{ "--accent": `var(--${action.accent})` }}
                >
                  <span className="material-symbols-outlined dash-action-icon">{action.icon}</span>
                  <span className="dash-action-label">{action.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* System status */}
          <div className="dash-system-card card-lift">
            <h2 className="dash-section-title">System Status</h2>
            <div className="dash-system-list">
              {[
                { label: "AI Prediction Engine", status: "online" },
                { label: "Satellite Feed", status: "online" },
                { label: "Alert Broadcast", status: "online" },
                { label: "Backend API", status: "pending" },
                { label: "Database",     status: "pending" },
              ].map((sys) => (
                <div key={sys.label} className="dash-system-row">
                  <span className="dash-system-label">{sys.label}</span>
                  <span className={`dash-system-dot dash-dot-${sys.status}`} />
                </div>
              ))}
            </div>
            <button
              className="btn-tonal"
              style={{width:"100%", marginTop:8}}
              id="btn-system-status"
              onClick={() => onNavigate("system-status")}
            >
              <span className="material-symbols-outlined">security</span>
              Full Status Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
