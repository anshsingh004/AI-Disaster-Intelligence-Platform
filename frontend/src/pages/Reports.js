import React, { useState } from "react";
import "./Reports.css";

const REPORTS = [
  {
    id: "RPT-8492",
    type: "Wildfire",
    icon: "local_fire_department",
    risk: "critical",
    location: "Sector 7G, Northern Ridge",
    timestamp: "Oct 24, 14:30Z",
    status: "active",
  },
  {
    id: "RPT-8491",
    type: "Flood Warning",
    icon: "water_drop",
    risk: "high",
    location: "River Valley Delta",
    timestamp: "Oct 24, 09:15Z",
    status: "monitoring",
  },
  {
    id: "RPT-8490",
    type: "Seismic Activity",
    icon: "landscape",
    risk: "medium",
    location: "Tectonic Fault Line B",
    timestamp: "Oct 23, 22:45Z",
    status: "resolved",
  },
  {
    id: "RPT-8489",
    type: "Cyclone",
    icon: "cyclone",
    risk: "critical",
    location: "Bay of Bengal Sector C",
    timestamp: "Oct 23, 18:00Z",
    status: "active",
  },
  {
    id: "RPT-8488",
    type: "Flood Warning",
    icon: "water_drop",
    risk: "medium",
    location: "Indus Delta, Sector 3",
    timestamp: "Oct 23, 12:30Z",
    status: "monitoring",
  },
];

const TYPE_OPTIONS = ["All Types", "Wildfire", "Flood", "Seismic", "Cyclone"];
const RISK_OPTIONS = ["All Risks", "Critical", "High", "Elevated"];

export default function Reports({ onNavigate }) {
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [riskFilter, setRiskFilter] = useState("All Risks");
  const [generating, setGenerating] = useState(false);

  const filtered = REPORTS.filter((r) => {
    const matchType = typeFilter === "All Types" || r.type.toLowerCase().includes(typeFilter.toLowerCase());
    const matchRisk = riskFilter === "All Risks" || r.risk === riskFilter.toLowerCase();
    return matchType && matchRisk;
  });

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => setGenerating(false), 3000);
  };

  return (
    <div className="reports-root fade-in">
      <header className="reports-header">
        <div>
          <h1 className="reports-title">Reports</h1>
          <p className="reports-sub">Manage and analyze recent incident documentation.</p>
        </div>
        <button id="btn-generate-report" className="btn-primary" onClick={handleGenerate}>
          <span className="material-symbols-outlined">add_circle</span>
          Generate New Report
        </button>
      </header>

      {/* Filters */}
      <div className="reports-filters">
        <div className="reports-search-wrap">
          <span className="material-symbols-outlined reports-search-icon">search</span>
          <input
            type="search"
            className="tech-input reports-search"
            placeholder="Search reports..."
          />
        </div>

        <select
          className="tech-input reports-select"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          {TYPE_OPTIONS.map((o) => <option key={o}>{o}</option>)}
        </select>

        <select
          className="tech-input reports-select"
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
        >
          {RISK_OPTIONS.map((o) => <option key={o}>{o}</option>)}
        </select>

        <button className="btn-tonal" onClick={() => onNavigate("backend-pending")}>
          <span className="material-symbols-outlined">calendar_today</span>
          Last 30 Days
        </button>
      </div>

      {/* Table */}
      <div className="reports-table-wrap card-lift">
        <table className="reports-table">
          <thead>
            <tr>
              <th>Report ID</th>
              <th>Type</th>
              <th>Risk Level</th>
              <th>Location</th>
              <th>Timestamp</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr
                key={r.id}
                className="reports-row"
                onClick={() => onNavigate("backend-pending")}
              >
                <td className="reports-id">{r.id}</td>
                <td>
                  <div className="reports-type-cell">
                    <span className="reports-type-icon">
                      <span className="material-symbols-outlined">{r.icon}</span>
                    </span>
                    {r.type}
                  </div>
                </td>
                <td>
                  <span className={`badge badge-${r.risk}`}>
                    {r.risk.charAt(0).toUpperCase() + r.risk.slice(1)}
                  </span>
                </td>
                <td className="reports-location">{r.location}</td>
                <td className="reports-time">{r.timestamp}</td>
                <td>
                  <span className={`badge badge-${r.status}`}>
                    {r.status.charAt(0).toUpperCase() + r.status.slice(1)}
                  </span>
                </td>
                <td>
                  <button
                    className="btn-icon"
                    id={`btn-view-${r.id}`}
                    onClick={(e) => { e.stopPropagation(); onNavigate("backend-pending"); }}
                    aria-label="View report"
                  >
                    <span className="material-symbols-outlined">chevron_right</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="reports-pagination">
          <span className="reports-count">Showing 1-{filtered.length} of 124 reports</span>
          <div className="reports-pag-btns">
            <button className="btn-icon" aria-label="Previous">
              <span className="material-symbols-outlined">chevron_left</span>
            </button>
            <button className="btn-icon" aria-label="Next">
              <span className="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="reports-footer">
        <span>© 2024 Terra-Aura Intelligence</span>
        <div className="reports-footer-links">
          {["Terms & Conditions", "Privacy Policy", "Contact", "Support"].map((l) => (
            <button key={l} className="reports-footer-link" onClick={() => onNavigate("legal")}>
              {l}
            </button>
          ))}
        </div>
      </footer>

      {/* Generate modal */}
      {generating && (
        <div className="modal-overlay" onClick={() => setGenerating(false)}>
          <div className="modal-card slide-in" onClick={(e) => e.stopPropagation()}>
            <span className="material-symbols-outlined modal-icon icon-fill">picture_as_pdf</span>
            <h3 className="modal-title">Generating Report</h3>
            <p className="modal-desc">Compiling incident data for Sector 7G, Northern Ridge. Your PDF will be ready shortly.</p>
            <div className="modal-spinner">
              <div className="spinner" />
            </div>
            <button className="btn-outline modal-cancel" onClick={() => setGenerating(false)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
