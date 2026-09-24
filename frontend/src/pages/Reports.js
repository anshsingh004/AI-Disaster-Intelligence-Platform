import React, { useState, useEffect, useCallback, useRef } from "react";
import "./Reports.css";
import { reportsApi, disastersApi } from "../services/api";
import { useNotifications } from "../context/NotificationContext";
import EmptyState from "../components/EmptyState";

const TYPE_OPTIONS = ["All Types", "Wildfire", "Flood Warning", "Seismic Activity", "Cyclone", "Fire", "Flood", "Earthquake"];
const RISK_OPTIONS = ["All Risks", "Critical", "High", "Medium", "Low"];
const STATUS_OPTIONS = ["All Statuses", "Active", "Monitoring", "Resolved"];

const riskIcon = (type) => {
  const icons = { Wildfire: "local_fire_department", Fire: "local_fire_department", "Flood Warning": "water_drop", Flood: "water_drop", "Seismic Activity": "landscape", Earthquake: "landscape", Cyclone: "cyclone" };
  return icons[type] || "description";
};

export default function Reports({ onNavigate, user }) {
  const [reports, setReports] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [riskFilter, setRiskFilter] = useState("All Risks");
  const [statusFilter, setStatusFilter] = useState("All Statuses");
  const [search, setSearch] = useState("");
  const searchTimer = useRef(null);

  // Generate Report modal state
  const [generating, setGenerating] = useState(false);
  const [disasters, setDisasters] = useState([]);
  const [genForm, setGenForm] = useState({ disaster_id: "", type: "", location: "", summary: "" });
  const [genError, setGenError] = useState("");
  const [genSubmitting, setGenSubmitting] = useState(false);

  // Delete confirmation state
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  // Expandable row state for AI report sections
  const [expandedRow, setExpandedRow] = useState(null);

  const { addNotification } = useNotifications();
  const canDelete = user?.role === "EOC_LEAD" || user?.role === "ADMINISTRATOR";

  const fetchReports = useCallback(async (currentPage = 1) => {
    setLoading(true);
    try {
      const params = { page: currentPage, limit: 10 };
      if (typeFilter !== "All Types") params.type = typeFilter;
      if (riskFilter !== "All Risks") params.risk = riskFilter.toLowerCase();
      if (statusFilter !== "All Statuses") params.status = statusFilter.toLowerCase();
      if (search.trim()) params.search = search.trim();

      const res = await reportsApi.list(params);
      setReports(res.data.data?.items || []);
      setTotal(res.data.data?.total || 0);
      setPages(res.data.data?.pages || 1);
    } catch (err) {
      console.error("Reports fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, [typeFilter, riskFilter, statusFilter, search]);

  useEffect(() => {
    setPage(1);
    fetchReports(1);
  }, [fetchReports]);

  // Debounced search handler
  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearch(val);
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => {
      setPage(1);
      fetchReports(1);
    }, 400);
  };

  // ── Generate report modal ──────────────────────────────────────────────────

  const openGenerateModal = async () => {
    setGenerating(true);
    setGenForm({ disaster_id: "", type: "", location: "", summary: "" });
    setGenError("");
    try {
      const res = await disastersApi.list({ limit: 20, sort_by: "created_at", order: "desc", refresh: true });
      setDisasters(res.data.data?.items || []);
    } catch (err) {
      setDisasters([]);
    }
  };

  const handleGenSubmit = async (e) => {
    e.preventDefault();
    if (!genForm.disaster_id || !genForm.type || !genForm.location) {
      setGenError("Disaster record, type, and location are required.");
      return;
    }
    setGenSubmitting(true);
    try {
      await reportsApi.create({
        disaster_id: parseInt(genForm.disaster_id),
        type: genForm.type,
        location: genForm.location,
        summary: genForm.summary || null,
      });
      setGenerating(false);
      fetchReports(page);
      addNotification({
        type: "report",
        title: `Report Generated — ${genForm.type}`,
        message: `Location: ${genForm.location}`,
      });
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to create report.";
      setGenError(msg);
    } finally {
      setGenSubmitting(false);
    }
  };

  // ── Delete report ──────────────────────────────────────────────────────────

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await reportsApi.delete(deleteTarget.id);
      setDeleteTarget(null);
      fetchReports(page);
    } catch (err) {
      console.error("Delete failed:", err);
    } finally {
      setDeleting(false);
    }
  };

  // ── Pagination ─────────────────────────────────────────────────────────────

  const goToPage = (p) => {
    if (p < 1 || p > pages) return;
    setPage(p);
    fetchReports(p);
  };

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="reports-root fade-in">
      <header className="reports-header">
        <div>
          <h1 className="reports-title">Reports</h1>
          <p className="reports-sub">Manage and analyze recent incident documentation.</p>
        </div>
        <button id="btn-generate-report" className="btn-primary" onClick={openGenerateModal}>
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
            placeholder="Search by type or location..."
            value={search}
            onChange={handleSearchChange}
          />
        </div>
        <select className="tech-input reports-select" value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1); }}>
          {TYPE_OPTIONS.map(o => <option key={o}>{o}</option>)}
        </select>
        <select className="tech-input reports-select" value={riskFilter} onChange={e => { setRiskFilter(e.target.value); setPage(1); }}>
          {RISK_OPTIONS.map(o => <option key={o}>{o}</option>)}
        </select>
        <select className="tech-input reports-select" value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }}>
          {STATUS_OPTIONS.map(o => <option key={o}>{o}</option>)}
        </select>
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
            {loading ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", padding: "32px 0", color: "var(--on-surface-variant)", fontSize: "13px" }}>
                  Loading reports...
                </td>
              </tr>
            ) : reports.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: "20px 0" }}>
                  <EmptyState
                    icon="description"
                    title="No Incident Reports Found"
                    subtitle={search || typeFilter !== "All Types" || riskFilter !== "All Risks" || statusFilter !== "All Statuses"
                      ? "No incident reports match your active search or filter criteria."
                      : "No situational intelligence reports have been compiled yet."}
                    actionLabel={search || typeFilter !== "All Types" || riskFilter !== "All Risks" || statusFilter !== "All Statuses" ? "Clear Filters" : undefined}
                    onAction={() => {
                      setSearch("");
                      setTypeFilter("All Types");
                      setRiskFilter("All Risks");
                      setStatusFilter("All Statuses");
                      setPage(1);
                    }}
                    compact
                  />
                </td>
              </tr>
            ) : (
              reports.map((r) => (
                <React.Fragment key={r.id}>
                  <tr
                    className={`reports-row${expandedRow === r.id ? " reports-row-expanded" : ""}`}
                    style={{ cursor: "pointer" }}
                    onClick={() => setExpandedRow(expandedRow === r.id ? null : r.id)}
                  >
                    <td className="reports-id">{r.report_code}</td>
                    <td>
                      <div className="reports-type-cell">
                        <span className="reports-type-icon">
                          <span className="material-symbols-outlined">{riskIcon(r.type)}</span>
                        </span>
                        {r.type}
                      </div>
                    </td>
                    <td>
                      <span className={`badge badge-${r.risk}`}>
                        {r.risk?.charAt(0).toUpperCase() + r.risk?.slice(1)}
                      </span>
                    </td>
                    <td className="reports-location">{r.location}</td>
                    <td className="reports-time">
                      {r.created_at ? new Date(r.created_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}
                    </td>
                    <td>
                      <span className={`badge badge-${r.status}`}>
                        {r.status?.charAt(0).toUpperCase() + r.status?.slice(1)}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 4 }} onClick={e => e.stopPropagation()}>
                        <button
                          className="btn-icon"
                          id={`btn-expand-${r.report_code}`}
                          onClick={() => setExpandedRow(expandedRow === r.id ? null : r.id)}
                          aria-label="Expand report"
                          title={expandedRow === r.id ? "Collapse" : "View full report"}
                        >
                          <span className="material-symbols-outlined">
                            {expandedRow === r.id ? "expand_less" : "expand_more"}
                          </span>
                        </button>
                        {canDelete && (
                          <button
                            className="btn-icon"
                            id={`btn-delete-${r.report_code}`}
                            onClick={() => setDeleteTarget(r)}
                            aria-label="Delete report"
                            title="Delete report"
                            style={{ color: "var(--error)" }}
                          >
                            <span className="material-symbols-outlined">delete</span>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                  {expandedRow === r.id && (
                    <tr className="reports-detail-row">
                      <td colSpan={7} style={{ padding: 0 }}>
                        <div className="reports-detail-panel">
                          <div className="rdp-header">
                            <span className="material-symbols-outlined rdp-header-icon">description</span>
                            <div>
                              <p className="rdp-title">AI Intelligence Report — {r.report_code}</p>
                              <p className="rdp-sub">Linked Incident #{r.disaster_id} · Generated {r.created_at ? new Date(r.created_at).toLocaleString() : "—"}</p>
                            </div>
                          </div>
                          {r.executive_summary ? (
                            <div className="rdp-sections">
                              {[
                                { key: "executive_summary",      label: "Executive Summary",       icon: "summarize" },
                                { key: "situation_analysis",     label: "Situation Analysis",      icon: "analytics" },
                                { key: "disaster_classification",label: "Disaster Classification", icon: "category" },
                                { key: "risk_assessment",        label: "Risk Assessment",         icon: "shield" },
                                { key: "population_impact",      label: "Population Impact",       icon: "groups" },
                                { key: "infrastructure_impact",  label: "Infrastructure Impact",  icon: "apartment" },
                                { key: "ai_confidence_note",     label: "AI Confidence",           icon: "smart_toy" },
                                { key: "forecast",               label: "Forecast / Expected Evolution", icon: "timeline" },
                                { key: "recommended_actions",    label: "Recommended Actions",    icon: "task_alt" },
                              ].filter(s => r[s.key]).map(s => (
                                <div key={s.key} className="rdp-section">
                                  <div className="rdp-section-header">
                                    <span className="material-symbols-outlined rdp-section-icon">{s.icon}</span>
                                    <span className="rdp-section-label">{s.label}</span>
                                  </div>
                                  <p className="rdp-section-text">{r[s.key]}</p>
                                </div>
                              ))}
                              {r.data_sources && (() => {
                                let sources = [];
                                try { sources = JSON.parse(r.data_sources); } catch {}
                                return sources.length > 0 ? (
                                  <div className="rdp-section">
                                    <div className="rdp-section-header">
                                      <span className="material-symbols-outlined rdp-section-icon">hub</span>
                                      <span className="rdp-section-label">Data Sources</span>
                                    </div>
                                    <div className="rdp-sources">
                                      {sources.map(src => (
                                        <span key={src} className="rdp-source-chip">{src}</span>
                                      ))}
                                    </div>
                                  </div>
                                ) : null;
                              })()}
                            </div>
                          ) : (
                            <p className="rdp-no-content">Full AI report content not available for this record. Regenerate the report to produce structured analysis.</p>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="reports-pagination">
          <span className="reports-count">
            {loading ? "Loading..." : `Showing ${reports.length} of ${total} reports`}
          </span>
          <div className="reports-pag-btns">
            <button className="btn-icon" aria-label="Previous" disabled={page <= 1} onClick={() => goToPage(page - 1)}>
              <span className="material-symbols-outlined">chevron_left</span>
            </button>
            <span style={{ fontSize: "13px", color: "var(--on-surface-variant)", padding: "0 8px" }}>
              {page} / {pages}
            </span>
            <button className="btn-icon" aria-label="Next" disabled={page >= pages} onClick={() => goToPage(page + 1)}>
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
            <button key={l} className="reports-footer-link" onClick={() => onNavigate("legal")}>{l}</button>
          ))}
        </div>
      </footer>

      {/* ── Generate Report Modal ── */}
      {generating && (
        <div className="modal-overlay" onClick={() => { setGenerating(false); setGenError(""); }}>
          <div className="modal-card slide-in" onClick={e => e.stopPropagation()} style={{ maxWidth: 460, width: "100%", gap: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span className="material-symbols-outlined modal-icon icon-fill" style={{ fontSize: 22, color: "var(--primary)" }}>picture_as_pdf</span>
              <h3 className="modal-title" style={{ margin: 0 }}>Generate New Report</h3>
            </div>
            {genError && (
              <div style={{ background: "rgba(176,38,20,0.1)", border: "1px solid var(--primary)", borderRadius: 8, padding: "10px 14px", fontSize: "13px", color: "var(--primary)" }}>
                {genError}
              </div>
            )}
            <form onSubmit={handleGenSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div className="signin-field">
                <label>Linked Disaster Record</label>
                <select
                  className="tech-input"
                  value={genForm.disaster_id}
                  onChange={e => setGenForm(p => ({ ...p, disaster_id: e.target.value }))}
                  required
                >
                  <option value="">Select a disaster...</option>
                  {disasters.map(d => (
                    <option key={d.id} value={d.id}>
                      #{d.id} — {d.disaster_type?.charAt(0).toUpperCase() + d.disaster_type?.slice(1)} ({d.risk_level})
                    </option>
                  ))}
                </select>
              </div>
              <div className="signin-field">
                <label>Report Type</label>
                <select
                  className="tech-input"
                  value={genForm.type}
                  onChange={e => setGenForm(p => ({ ...p, type: e.target.value }))}
                  required
                >
                  <option value="">Select type...</option>
                  {["Wildfire", "Flood Warning", "Seismic Activity", "Cyclone", "Drought", "Landslide", "Tsunami"].map(t => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div className="signin-field">
                <label>Location / Sector</label>
                <input
                  type="text"
                  className="tech-input"
                  placeholder="e.g. Sector 7G, Northern Ridge"
                  value={genForm.location}
                  onChange={e => setGenForm(p => ({ ...p, location: e.target.value }))}
                  required
                />
              </div>
              <div className="signin-field">
                <label>Summary (optional)</label>
                <textarea
                  className="tech-input"
                  rows={2}
                  placeholder="Brief situational summary..."
                  value={genForm.summary}
                  onChange={e => setGenForm(p => ({ ...p, summary: e.target.value }))}
                />
              </div>
              <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
                <button type="submit" id="btn-confirm-generate" className="btn-primary" style={{ flex: 1 }} disabled={genSubmitting}>
                  <span className="material-symbols-outlined">{genSubmitting ? "hourglass_empty" : "add_circle"}</span>
                  {genSubmitting ? "Creating..." : "Create Report"}
                </button>
                <button type="button" className="btn-outline modal-cancel" onClick={() => { setGenerating(false); setGenError(""); }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Delete Confirmation Modal ── */}
      {deleteTarget && (
        <div className="modal-overlay" onClick={() => setDeleteTarget(null)}>
          <div className="modal-card slide-in" onClick={e => e.stopPropagation()} style={{ maxWidth: 400, textAlign: "center" }}>
            <span className="material-symbols-outlined modal-icon" style={{ fontSize: 36, color: "var(--error)" }}>delete_forever</span>
            <h3 className="modal-title">Delete Report</h3>
            <p className="modal-desc">
              Permanently delete <strong>{deleteTarget.report_code}</strong>? This action cannot be undone.
            </p>
            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button className="btn-danger" style={{ flex: 1 }} onClick={handleDelete} disabled={deleting}>
                {deleting ? "Deleting..." : "Delete"}
              </button>
              <button className="btn-outline" style={{ flex: 1 }} onClick={() => setDeleteTarget(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
