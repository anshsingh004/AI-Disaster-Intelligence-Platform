import React from "react";
import "./Analytics.css";

const BAR_DATA = [
  { month: "Jan", val: 45 },
  { month: "Feb", val: 62 },
  { month: "Mar", val: 55 },
  { month: "Apr", val: 80 },
  { month: "May", val: 70 },
  { month: "Jun", val: 58 },
];

const SECTORS = [
  { name: "Infrastructure", risk: 82, color: "var(--primary)" },
  { name: "Agriculture",    risk: 65, color: "var(--secondary)" },
  { name: "Health",         risk: 51, color: "var(--tertiary)" },
  { name: "Transport",      risk: 74, color: "var(--primary-container)" },
  { name: "Energy",         risk: 43, color: "var(--outline)" },
];

export default function Analytics({ onNavigate }) {
  return (
    <div className="analytics-root fade-in">
      <header className="analytics-header">
        <div>
          <h1 className="analytics-title">Analytics</h1>
          <p className="analytics-sub">Disaster trends and insights overview</p>
        </div>
        <button id="btn-data-export" className="btn-primary" onClick={() => onNavigate("backend-pending")}>
          <span className="material-symbols-outlined">download</span>
          Data Export
        </button>
      </header>

      {/* KPI Cards */}
      <div className="analytics-kpi-grid">
        <div className="analytics-kpi card-lift">
          <p className="kpi-label">Avg Confidence</p>
          <p className="kpi-value">85%</p>
          <div className="kpi-trend kpi-up">
            <span className="material-symbols-outlined" style={{fontSize:16}}>trending_up</span>
            <span>+5%</span>
          </div>
        </div>
        <div className="analytics-kpi card-lift">
          <p className="kpi-label">Response Efficiency</p>
          <p className="kpi-value">92%</p>
          <div className="kpi-trend kpi-up">
            <span className="material-symbols-outlined" style={{fontSize:16}}>trending_up</span>
            <span>+2%</span>
          </div>
        </div>
        <div className="analytics-kpi card-lift">
          <p className="kpi-label">Regional Stability Index</p>
          <p className="kpi-value">0.75</p>
          <div className="kpi-trend kpi-down">
            <span className="material-symbols-outlined" style={{fontSize:16}}>trending_down</span>
            <span>-0.05</span>
          </div>
        </div>
        <div className="analytics-kpi card-lift" onClick={() => onNavigate("backend-pending")} style={{cursor:"pointer"}}>
          <p className="kpi-label">Active Incidents</p>
          <p className="kpi-value">124</p>
          <div className="kpi-trend kpi-neutral">
            <span className="material-symbols-outlined" style={{fontSize:16}}>remove</span>
            <span>Stable</span>
          </div>
        </div>
      </div>

      <div className="analytics-charts-grid">
        {/* Severity Trend bar chart */}
        <div className="analytics-chart-card card-lift">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Severity Trends Over Time</h2>
              <p className="chart-sub">Overall disaster severity index — last 6 months</p>
            </div>
            <span className="badge badge-critical">High Alert</span>
          </div>
          <div className="bar-chart">
            {BAR_DATA.map((d) => (
              <div key={d.month} className="bar-col">
                <div className="bar-fill-wrap">
                  <div
                    className="bar-fill"
                    style={{ height: `${d.val}%` }}
                    title={`${d.month}: ${d.val}`}
                  />
                </div>
                <span className="bar-label">{d.month}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pie chart */}
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
              {[
                { label: "Flood", pct: "45%", color: "var(--primary)" },
                { label: "Fire",  pct: "30%", color: "var(--secondary)" },
                { label: "Earthquake", pct: "15%", color: "var(--tertiary)" },
                { label: "Storm", pct: "10%", color: "var(--outline)" },
              ].map((l) => (
                <div key={l.label} className="pie-legend-item">
                  <span className="pie-dot" style={{ background: l.color }} />
                  <span className="pie-legend-text">{l.label} ({l.pct})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Risk distribution */}
      <div className="analytics-risk-card card-lift">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">Risk Distribution by Sector</h2>
            <p className="chart-sub">Vulnerability assessment across key infrastructure</p>
          </div>
          <button id="btn-full-report" className="btn-tonal" onClick={() => onNavigate("reports")}>
            <span className="material-symbols-outlined">description</span>
            Full Report
          </button>
        </div>
        <div className="risk-rows">
          {SECTORS.map((s) => (
            <div key={s.name} className="risk-row">
              <span className="risk-row-name">{s.name}</span>
              <div className="progress-track" style={{ flex: 1 }}>
                <div
                  className="progress-fill"
                  style={{ width: `${s.risk}%`, background: s.color }}
                />
              </div>
              <span className="risk-row-val" style={{ color: s.color }}>{s.risk}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
