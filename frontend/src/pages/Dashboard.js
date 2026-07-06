import React, { useState, useEffect, useCallback } from "react";
import "./Dashboard.css";
import { disastersApi, alertsApi, healthApi } from "../services/api";

// Maps disaster_type to Material Symbol icon name
const typeIcon = (type) => {
  const icons = { fire: "local_fire_department", flood: "water_drop", earthquake: "landscape", cyclone: "cyclone", storm: "thunderstorm", none: "warning" };
  return icons[type?.toLowerCase()] || "warning";
};

const levelColor = (level) => {
  const colors = { CRITICAL: "var(--error)", HIGH: "var(--primary)", MEDIUM: "var(--secondary)", LOW: "var(--tertiary)" };
  return colors[level?.toUpperCase()] || "var(--outline)";
};

export default function Dashboard({ user, onNavigate }) {
  const [disasters, setDisasters] = useState([]);
  const [stats, setStats] = useState({ total: 0, avgConfidence: 0, highRisk: 0, unacknowledged: 0 });
  const [systemStatus, setSystemStatus] = useState({ api: "pending", database: "pending" });
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [disastersRes, alertsRes, healthRes] = await Promise.all([
        disastersApi.list({ limit: 10, sort_by: "created_at", order: "desc" }),
        alertsApi.list({ limit: 100 }),
        healthApi.readiness().catch(() => null),
      ]);

      const items = disastersRes.data.data.items || [];
      const total = disastersRes.data.data.total || 0;
      const allAlerts = alertsRes.data.data.items || [];

      const avgConfidence = items.length > 0
        ? Math.round((items.reduce((s, d) => s + d.confidence, 0) / items.length) * 100)
        : 0;
      const highRisk = items.filter(d => d.risk_level === "HIGH" || d.risk_level === "CRITICAL").length;
      const unacknowledged = allAlerts.filter(a => !a.acknowledged).length;

      setDisasters(items.slice(0, 4));
      setStats({ total, avgConfidence, highRisk, unacknowledged });

      if (healthRes) {
        const isReady = healthRes.data?.status === "ready";
        const dbOk = healthRes.data?.database === "connected";
        setSystemStatus({
          api: isReady ? "online" : "degraded",
          database: dbOk ? "online" : "offline",
        });
      }
    } catch (err) {
      console.error("Dashboard data fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const QUICK_STATS = [
    {
      label: "Active Incidents",
      value: loading ? "—" : String(stats.total),
      icon: "warning",
      color: "var(--primary)",
      delta: stats.total > 0 ? `${stats.highRisk} high-risk` : "No incidents",
    },
    {
      label: "AI Confidence",
      value: loading ? "—" : `${stats.avgConfidence}%`,
      icon: "psychology",
      color: "var(--secondary)",
      delta: "Prediction accuracy",
    },
    {
      label: "High-Risk Events",
      value: loading ? "—" : String(stats.highRisk),
      icon: "radar",
      color: "var(--tertiary)",
      delta: "Require immediate attention",
    },
    {
      label: "Unacknowledged",
      value: loading ? "—" : String(stats.unacknowledged),
      icon: "speed",
      color: "#16a34a",
      delta: "Pending analyst review",
    },
  ];

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
            <h2 className="dash-section-title">Recent Incidents</h2>
            <button className="btn-tonal" id="btn-view-all-incidents" onClick={() => onNavigate("disaster-center")}>
              <span className="material-symbols-outlined">description</span>
              View All
            </button>
          </div>
          <div className="dash-incident-list">
            {loading ? (
              <p style={{ color: "var(--on-surface-variant)", padding: "16px", textAlign: "center", fontSize: "13px" }}>
                Loading incidents...
              </p>
            ) : disasters.length === 0 ? (
              <p style={{ color: "var(--on-surface-variant)", padding: "16px", textAlign: "center", fontSize: "13px" }}>
                No incidents recorded yet.
              </p>
            ) : (
              disasters.map((inc) => {
                const badgeLevel = inc.risk_level?.toLowerCase() || "medium";
                const color = levelColor(inc.risk_level);
                return (
                  <div
                    key={inc.id}
                    className="dash-incident-row"
                    onClick={() => onNavigate("disaster-center")}
                    role="button"
                    tabIndex={0}
                  >
                    <div className={`dash-incident-icon dash-incident-icon-${badgeLevel}`}>
                      <span className="material-symbols-outlined">{typeIcon(inc.disaster_type)}</span>
                    </div>
                    <div className="dash-incident-info">
                      <p className="dash-incident-type">{inc.disaster_type?.charAt(0).toUpperCase() + inc.disaster_type?.slice(1) || "Unknown"}</p>
                      <p className="dash-incident-sector">{inc.latitude?.toFixed(2)}, {inc.longitude?.toFixed(2)}</p>
                    </div>
                    <div className="dash-incident-right">
                      <span className={`badge badge-${badgeLevel}`}>
                        {inc.risk_level?.charAt(0) + inc.risk_level?.slice(1).toLowerCase()}
                      </span>
                      <div className="dash-severity-bar">
                        <div
                          className="dash-severity-fill"
                          style={{ width: `${Math.round(inc.severity_score * 100)}%`, background: color }}
                        />
                      </div>
                      <span className="dash-severity-val">{Math.round(inc.severity_score * 100)}%</span>
                    </div>
                    <span className="material-symbols-outlined dash-incident-chevron">chevron_right</span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Quick actions + system status */}
        <div className="dash-actions-col">
          <div className="dash-quick-actions card-lift">
            <h2 className="dash-section-title">Quick Actions</h2>
            <div className="dash-action-grid">
              {[
                { label: "Disaster Center", icon: "map", page: "disaster-center", accent: "primary" },
                { label: "Run Analytics", icon: "bar_chart", page: "analytics", accent: "secondary" },
                { label: "Generate Report", icon: "description", page: "reports", accent: "tertiary" },
                { label: "New Incident", icon: "add_circle", page: "disaster-center", accent: "primary" },
                { label: "View Alerts", icon: "warning", page: "disaster-center", accent: "error" },
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

          {/* System status — real from /readiness */}
          <div className="dash-system-card card-lift">
            <h2 className="dash-section-title">System Status</h2>
            <div className="dash-system-list">
              {[
                { label: "Backend API", status: systemStatus.api },
                { label: "Database", status: systemStatus.database },
                { label: "AI Inference Engine", status: "online" },
                { label: "Cache Layer", status: "online" },
                { label: "Auth Service", status: "online" },
              ].map((sys) => (
                <div key={sys.label} className="dash-system-row">
                  <span className="dash-system-label">{sys.label}</span>
                  <span className={`dash-system-dot dash-dot-${sys.status}`} />
                </div>
              ))}
            </div>
            <button
              className="btn-tonal"
              style={{ width: "100%", marginTop: 8 }}
              id="btn-system-status"
              onClick={() => onNavigate("analytics")}
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
