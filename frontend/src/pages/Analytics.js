import React, { useState, useEffect, useCallback } from "react";
import "./Analytics.css";
import { disastersApi, reportsApi } from "../services/api";

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Groups disasters by disaster_type and computes average severity per type */
const groupBySeverity = (disasters) => {
  const groups = {};
  disasters.forEach(d => {
    const type = d.disaster_type || "none";
    if (!groups[type]) groups[type] = { total: 0, count: 0 };
    groups[type].total += d.severity_score || 0;
    groups[type].count += 1;
  });
  return Object.entries(groups).map(([type, { total, count }]) => ({
    type: type.charAt(0).toUpperCase() + type.slice(1),
    avg: Math.round((total / count) * 100),
  }));
};

/** Counts disasters by risk_level */
const groupByRisk = (disasters) => {
  const palette = {
    CRITICAL: "var(--primary)",
    HIGH: "var(--secondary)",
    MEDIUM: "var(--tertiary)",
    LOW: "var(--outline)",
  };
  const counts = {};
  disasters.forEach(d => {
    counts[d.risk_level] = (counts[d.risk_level] || 0) + 1;
  });
  const total = disasters.length || 1;
  return Object.entries(counts).map(([level, count]) => ({
    name: level.charAt(0) + level.slice(1).toLowerCase(),
    risk: Math.round((count / total) * 100),
    color: palette[level] || "var(--outline)",
  }));
};

/** Type distribution for pie legend */
const groupByType = (disasters) => {
  const palette = ["var(--primary)", "var(--secondary)", "var(--tertiary)", "var(--outline)"];
  const counts = {};
  disasters.forEach(d => { counts[d.disaster_type || "none"] = (counts[d.disaster_type || "none"] || 0) + 1; });
  const total = disasters.length || 1;
  return Object.entries(counts).map(([type, count], i) => ({
    label: type.charAt(0).toUpperCase() + type.slice(1),
    pct: `${Math.round((count / total) * 100)}%`,
    color: palette[i % palette.length],
  }));
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function Analytics({ onNavigate }) {
  const [disasters, setDisasters] = useState([]);
  const [reportsTotal, setReportsTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [disastersRes, reportsRes] = await Promise.all([
        disastersApi.list({ limit: 100, sort_by: "created_at", order: "desc" }),
        reportsApi.list({ limit: 1 }),
      ]);
      setDisasters(disastersRes.data.data?.items || []);
      setReportsTotal(reportsRes.data.data?.total || 0);
    } catch (err) {
      console.error("Analytics fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // ── Derived metrics ────────────────────────────────────────────────────────
  const total = disasters.length;
  const avgConfidence = total > 0
    ? Math.round((disasters.reduce((s, d) => s + (d.confidence || 0), 0) / total) * 100)
    : 0;
  const avgSeverity = total > 0
    ? (disasters.reduce((s, d) => s + (d.severity_score || 0), 0) / total).toFixed(2)
    : "—";
  const activeCount = disasters.filter(d => d.risk_level === "HIGH" || d.risk_level === "CRITICAL").length;

  const barData = groupBySeverity(disasters);
  const riskRows = groupByRisk(disasters);
  const typeData = groupByType(disasters);

  const KPI_CARDS = [
    {
      label: "Avg Confidence",
      value: loading ? "—" : `${avgConfidence}%`,
      trend: total > 0 ? "kpi-up" : "kpi-neutral",
      trendIcon: "trending_up",
      trendText: `${total} predictions`,
    },
    {
      label: "Avg Severity",
      value: loading ? "—" : avgSeverity,
      trend: parseFloat(avgSeverity) > 0.7 ? "kpi-down" : "kpi-up",
      trendIcon: parseFloat(avgSeverity) > 0.7 ? "trending_up" : "trending_down",
      trendText: "severity index",
    },
    {
      label: "High-Risk Events",
      value: loading ? "—" : String(activeCount),
      trend: activeCount > 0 ? "kpi-down" : "kpi-up",
      trendIcon: activeCount > 0 ? "trending_up" : "remove",
      trendText: "require attention",
    },
    {
      label: "Incident Reports",
      value: loading ? "—" : String(reportsTotal),
      trend: "kpi-neutral",
      trendIcon: "remove",
      trendText: "filed reports",
    },
  ];

  return (
    <div className="analytics-root fade-in">
      <header className="analytics-header">
        <div>
          <h1 className="analytics-title">Analytics</h1>
          <p className="analytics-sub">Disaster trends and insights overview</p>
        </div>
        <button
          id="btn-data-export"
          className="btn-primary"
          onClick={() => onNavigate("reports")}
          title="Export data is available via the Reports module"
        >
          <span className="material-symbols-outlined">description</span>
          View Reports
        </button>
      </header>

      {/* KPI Cards */}
      <div className="analytics-kpi-grid">
        {KPI_CARDS.map((kpi) => (
          <div key={kpi.label} className="analytics-kpi card-lift">
            <p className="kpi-label">{kpi.label}</p>
            <p className="kpi-value">{kpi.value}</p>
            <div className={`kpi-trend ${kpi.trend}`}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{kpi.trendIcon}</span>
              <span>{kpi.trendText}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="analytics-charts-grid">
        {/* Severity by type bar chart */}
        <div className="analytics-chart-card card-lift">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Severity by Disaster Type</h2>
              <p className="chart-sub">Average severity index per disaster category</p>
            </div>
            {activeCount > 0 && <span className="badge badge-critical">High Alert</span>}
          </div>
          {loading ? (
            <p style={{ textAlign: "center", color: "var(--on-surface-variant)", fontSize: "13px", padding: "32px 0" }}>Loading chart...</p>
          ) : barData.length === 0 ? (
            <p style={{ textAlign: "center", color: "var(--on-surface-variant)", fontSize: "13px", padding: "32px 0" }}>No incident data yet.</p>
          ) : (
            <div className="bar-chart">
              {barData.map((d) => (
                <div key={d.type} className="bar-col">
                  <div className="bar-fill-wrap">
                    <div className="bar-fill" style={{ height: `${d.avg}%` }} title={`${d.type}: ${d.avg}%`} />
                  </div>
                  <span className="bar-label">{d.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Type frequency pie legend */}
        <div className="analytics-chart-card card-lift">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Type Frequency</h2>
              <p className="chart-sub">Distribution of recorded events</p>
            </div>
          </div>
          <div className="pie-chart-wrap">
            <div className="pie-chart" />
            <div className="pie-legend">
              {loading ? (
                <p style={{ fontSize: "13px", color: "var(--on-surface-variant)" }}>Loading...</p>
              ) : typeData.length === 0 ? (
                <p style={{ fontSize: "13px", color: "var(--on-surface-variant)" }}>No data available.</p>
              ) : (
                typeData.map((l) => (
                  <div key={l.label} className="pie-legend-item">
                    <span className="pie-dot" style={{ background: l.color }} />
                    <span className="pie-legend-text">{l.label} ({l.pct})</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Risk distribution */}
      <div className="analytics-risk-card card-lift">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">Risk Distribution</h2>
            <p className="chart-sub">Proportion of incidents by risk classification</p>
          </div>
          <button id="btn-full-report" className="btn-tonal" onClick={() => onNavigate("reports")}>
            <span className="material-symbols-outlined">description</span>
            Full Report
          </button>
        </div>
        <div className="risk-rows">
          {loading ? (
            <p style={{ textAlign: "center", color: "var(--on-surface-variant)", fontSize: "13px", padding: "16px 0" }}>Loading...</p>
          ) : riskRows.length === 0 ? (
            <p style={{ textAlign: "center", color: "var(--on-surface-variant)", fontSize: "13px", padding: "16px 0" }}>No incidents recorded yet.</p>
          ) : (
            riskRows.map((s) => (
              <div key={s.name} className="risk-row">
                <span className="risk-row-name">{s.name}</span>
                <div className="progress-track" style={{ flex: 1 }}>
                  <div className="progress-fill" style={{ width: `${s.risk}%`, background: s.color }} />
                </div>
                <span className="risk-row-val" style={{ color: s.color }}>{s.risk}%</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
