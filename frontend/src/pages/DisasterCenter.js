import React, { useState, useEffect, useCallback } from "react";
import "./DisasterCenter.css";
import { alertsApi, disastersApi, feedsApi } from "../services/api";
import DisasterMap from "../DisasterMap";
import { useNotifications } from "../context/NotificationContext";
import EmptyState from "../components/EmptyState";
import SitrepDossierDrawer from "../components/SitrepDossierDrawer";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const typeIcon = (type) => {
  const icons = { fire: "local_fire_department", flood: "water_drop", earthquake: "landscape", cyclone: "cyclone", storm: "thunderstorm" };
  return icons[type?.toLowerCase()] || "warning";
};

const timeAgo = (isoStr) => {
  if (!isoStr) return "—";
  const diff = (Date.now() - new Date(isoStr)) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hrs ago`;
  return new Date(isoStr).toLocaleDateString();
};

const INITIAL_FORM = {
  disaster_type: "flood",
  title: "",
  latitude: "",
  longitude: "",
  weather_rainfall: "80.0",
  weather_wind_speed: "25.0",
  social_signal_score: "0.75",
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function DisasterCenter({ user, onNavigate, focusUnacknowledged, onFocusHandled }) {
  const [alerts, setAlerts] = useState([]);
  const [disasters, setDisasters] = useState([]);
  const [activeAlert, setActiveAlert] = useState(null);
  const [aiOpen, setAiOpen] = useState(true);
  const [loading, setLoading] = useState(true);
  const [dossierIncident, setDossierIncident] = useState(null);

  const { addNotification } = useNotifications();

  // New incident form state
  const [newIncidentOpen, setNewIncidentOpen] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Inline toast for deferred/informational actions
  const [toast, setToast] = useState(null);
  const [scanningFeeds, setScanningFeeds] = useState(false);

  const showToast = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4500);
  }, []);

  const handleIncidentAcknowledged = (incidentId) => {
    setDisasters(prev => prev.map(d => d.id === incidentId ? { ...d, acknowledged: true } : d));
    setAlerts(prev => prev.map(a => a.disaster_id === incidentId ? { ...a, acknowledged: true } : a));
    if (activeAlert?.disaster_id === incidentId) {
      setActiveAlert(prev => ({ ...prev, acknowledged: true }));
    }
    if (dossierIncident?.id === incidentId) {
      setDossierIncident(prev => ({ ...prev, acknowledged: true }));
    }
    showToast("Incident operational status updated to Acknowledged.");
  };

  const handleScanPublicFeeds = async () => {
    setScanningFeeds(true);
    try {
      const res = await feedsApi.scan({ min_magnitude: 1.0 });
      const data = res.data?.data || {};
      const { scanned = 0, new_ingested = 0, events = [] } = data;
      if (new_ingested > 0) {
        addNotification({
          type: "success",
          title: "Public Feeds Ingested",
          message: `Identified ${scanned} USGS events. Ingested ${new_ingested} verified emergency incidents with AI SITREPs.`,
        });
        await fetchData(events[0]?.id, true);
      } else {
        addNotification({
          type: "info",
          title: "Feeds Scanned",
          message: `Scanned ${scanned} USGS seismic feeds. No new incidents to ingest (existing items already tracked).`,
        });
      }
    } catch (err) {
      addNotification({
        type: "error",
        title: "Feed Ingestion Failed",
        message: err.response?.data?.detail || "Could not complete public feed scan. External network may be unavailable.",
      });
    } finally {
      setScanningFeeds(false);
    }
  };

  const fetchData = useCallback(async (selectDisasterId = null, forceRefresh = false) => {
    try {
      const params = { limit: 50, sort_by: "created_at", order: "desc" };
      if (forceRefresh) {
        params.refresh = true;
      }
      const [alertsRes, disastersRes] = await Promise.all([
        alertsApi.list({ limit: 50 }),
        disastersApi.list(params),
      ]);
      const alertItems = alertsRes.data.data?.items || [];
      const disasterItems = disastersRes.data.data?.items || [];

      setAlerts(alertItems);
      setDisasters(disasterItems);
      
      setActiveAlert(prev => {
        if (selectDisasterId) {
          const linked = alertItems.find(a => a.disaster_id === selectDisasterId);
          if (linked) return linked;
        }
        if (prev) {
          const freshActive = alertItems.find(a => a.id === prev.id);
          if (freshActive) return freshActive;
        }
        return alertItems[0] || null;
      });
    } catch (err) {
      console.error("DisasterCenter fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchData(); }, [fetchData]);

  // Auto-select first unacknowledged alert when navigated from Dashboard
  useEffect(() => {
    if (focusUnacknowledged && alerts.length > 0 && !loading) {
      const unacked = alerts.find(a => !a.acknowledged);
      if (unacked) setActiveAlert(unacked);
      if (onFocusHandled) onFocusHandled();
    }
  }, [focusUnacknowledged, alerts, loading, onFocusHandled]);

  // ── Acknowledge alert ──────────────────────────────────────────────────────

  const handleAck = async (id) => {
    try {
      await alertsApi.acknowledge(id);
      const updated = alerts.map(a => a.id === id ? { ...a, acknowledged: true } : a);
      setAlerts(updated);
      if (activeAlert?.id === id) setActiveAlert(prev => ({ ...prev, acknowledged: true }));
    } catch (err) {
      showToast("Failed to acknowledge alert. Please try again.");
    }
  };

  // ── New incident form ──────────────────────────────────────────────────────

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    if (name === "disaster_type") {
      // Adjust default baseline telemetry based on selected disaster type
      const defaults = {
        flood: { weather_rainfall: "85.0", weather_wind_speed: "25.0", social_signal_score: "0.8" },
        fire: { weather_rainfall: "5.0", weather_wind_speed: "65.0", social_signal_score: "0.75" },
        earthquake: { weather_rainfall: "0.0", weather_wind_speed: "10.0", social_signal_score: "0.85" },
        storm: { weather_rainfall: "50.0", weather_wind_speed: "95.0", social_signal_score: "0.7" },
      };
      setForm(prev => ({ ...prev, disaster_type: value, ...(defaults[value] || {}) }));
    } else {
      setForm(prev => ({ ...prev, [name]: value }));
    }
    setFormError("");
  };

  const handleNewIncidentSubmit = async (e) => {
    e.preventDefault();
    const { title, latitude, longitude, weather_rainfall, weather_wind_speed, social_signal_score } = form;

    const lat = parseFloat(latitude);
    const lng = parseFloat(longitude);
    const rainfall = parseFloat(weather_rainfall);
    const wind = parseFloat(weather_wind_speed);
    const social = parseFloat(social_signal_score);

    if ([lat, lng, rainfall, wind, social].some(isNaN)) {
      setFormError("All numerical telemetry fields are required and must be valid numbers.");
      return;
    }
    if (lat < -90 || lat > 90) { setFormError("Latitude must be between -90 and 90."); return; }
    if (lng < -180 || lng > 180) { setFormError("Longitude must be between -180 and 180."); return; }
    if (social < 0 || social > 1) { setFormError("Social signal score must be between 0.0 and 1.0."); return; }

    setSubmitting(true);
    try {
      const response = await disastersApi.create({
        title: title?.trim() || undefined,
        latitude: lat,
        longitude: lng,
        timestamp: new Date().toISOString(),
        weather_rainfall: rainfall,
        weather_wind_speed: wind,
        social_signal_score: social,
        source_origin: "MANUAL",
      });
      const newDisaster = response.data.data;
      setNewIncidentOpen(false);
      setForm(INITIAL_FORM);
      setFormError("");
      await fetchData(newDisaster?.id, true);
      showToast("New incident analyzed and recorded successfully.");
      // Emit notifications
      addNotification({
        type: "incident",
        title: `Incident Created — ${newDisaster?.disaster_type?.charAt(0).toUpperCase() + newDisaster?.disaster_type?.slice(1) || "Unknown"}`,
        message: `Risk: ${newDisaster?.risk_level} · Severity: ${Math.round((newDisaster?.severity_score || 0) * 100)}%`,
      });
      if (newDisaster?.risk_level === "HIGH" || newDisaster?.risk_level === "CRITICAL") {
        addNotification({
          type: "alert",
          title: `${newDisaster.risk_level} Risk Alert`,
          message: `${newDisaster.disaster_type} event detected — auto-report generated.`,
        });
      }
    } catch (err) {
      setFormError(err.response?.data?.detail || "Submission failed. Please check parameters.");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Select disaster from map click ────────────────────────────────────────

  const handleMapDisasterSelect = (disaster) => {
    const linked = alerts.find(a => a.disaster_id === disaster.id);
    if (linked) setActiveAlert(linked);
  };

  // ─── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="dc-root fade-in">
      {/* ── Top bar ── */}
      <header className="dc-topbar">
        <div className="dc-topbar-left">
          <div className="dc-live-badge">
            <span className="pulse-dot" />
            <span>Live Sync Active</span>
          </div>
          <span className="dc-sector-label">
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>location_on</span>
            {loading ? "Loading..." : `${alerts.length} alerts · ${disasters.length} incidents tracked`}
          </span>
        </div>
        <div className="dc-topbar-right">
          <button
            id="btn-scan-feeds"
            className="btn-tonal"
            onClick={handleScanPublicFeeds}
            disabled={scanningFeeds}
            title="Scan live USGS earthquakes and Open-Meteo atmospheric feeds"
          >
            <span className={`material-symbols-outlined${scanningFeeds ? " spin" : ""}`}>
              {scanningFeeds ? "sync" : "rss_feed"}
            </span>
            {scanningFeeds ? "Scanning Feeds..." : "Scan Public Feeds"}
          </button>
          <button id="btn-new-incident" className="btn-primary" onClick={() => setNewIncidentOpen(true)}>
            <span className="material-symbols-outlined">add_circle</span>
            New Incident
          </button>
          <button className="btn-icon" aria-label="View Reports" onClick={() => onNavigate("reports")}>
            <span className="material-symbols-outlined">description</span>
          </button>

        </div>
      </header>

      {/* ── Toast notification ── */}
      {toast && (
        <div style={{
          position: "fixed",
          top: 24,
          right: 24,
          zIndex: 9999,
          background: "var(--surface-container)",
          border: "1px solid var(--outline-variant)",
          borderLeft: "4px solid var(--secondary)",
          borderRadius: "8px",
          padding: "14px 18px",
          maxWidth: "360px",
          fontSize: "13px",
          color: "var(--on-surface)",
          boxShadow: "var(--shadow-lg)",
          display: "flex",
          alignItems: "flex-start",
          gap: "10px",
          lineHeight: 1.5,
        }}>
          <span className="material-symbols-outlined" style={{ fontSize: 18, color: "var(--secondary)", flexShrink: 0 }}>info</span>
          <span>{toast}</span>
        </div>
      )}

      <div className="dc-body">
        {/* ── Map panel with real Leaflet map ── */}
        <div className="dc-map-panel">
          {loading ? (
            <div className="dc-map-bg" style={{ display: "flex", alignItems: "center", justifyContent: "center", color: "var(--on-surface-variant)", fontSize: "13px", gap: 8 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>radar</span>
              Loading incident map...
            </div>
          ) : (
            <DisasterMap
              disasters={disasters}
              onSelectDisaster={handleMapDisasterSelect}
              onOpenDossier={(d) => setDossierIncident(d)}
            />
          )}

          <div className="dc-map-controls">
            <button className="btn-icon dc-map-btn" onClick={() => fetchData(null, true)} aria-label="Refresh map">
              <span className="material-symbols-outlined">refresh</span>
            </button>
          </div>
          <div className="dc-map-label">Disaster Center — Global Monitoring · {disasters.length} incidents</div>
        </div>

        {/* ── AI / Alerts panel ── */}
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
              {loading ? (
                <p style={{ color: "var(--on-surface-variant)", padding: "24px 16px", textAlign: "center", fontSize: "13px" }}>
                  Loading alerts...
                </p>
              ) : alerts.length === 0 ? (
                <EmptyState
                  icon="shield"
                  title="No Active Incident Alerts"
                  subtitle="All operational sectors reporting normal telemetry."
                  compact
                />
              ) : (
                <>
                  {/* Alert selector tabs */}
                  <div className="dc-alert-tabs">
                    {alerts.slice(0, 5).map(a => (
                      <button
                        key={a.id}
                        className={`dc-alert-tab${activeAlert?.id === a.id ? " active" : ""} dc-alert-tab-${a.level?.toLowerCase()}`}
                        onClick={() => setActiveAlert(a)}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                          {typeIcon(a.disaster_type)}
                        </span>
                        <span className={`badge badge-${a.level?.toLowerCase()}`}>
                          {a.level?.charAt(0) + a.level?.slice(1).toLowerCase()}
                        </span>
                        <span className="dc-alert-tab-time">{timeAgo(a.created_at)}</span>
                      </button>
                    ))}
                  </div>

                  {/* Active alert detail card */}
                  {activeAlert && (
                    <div className="dc-alert-card">
                      <div className="dc-alert-card-header">
                        <span className={`badge badge-${activeAlert.level?.toLowerCase()}`}>
                          <span className="material-symbols-outlined" style={{ fontSize: 11 }}>warning</span>
                          {activeAlert.level?.charAt(0) + activeAlert.level?.slice(1).toLowerCase()} Alert
                        </span>
                        <span className="dc-alert-time">{timeAgo(activeAlert.created_at)}</span>
                      </div>
                      <h3 className="dc-alert-title">{activeAlert.title}</h3>
                      <p className="dc-alert-desc">{activeAlert.description || "No additional description available."}</p>

                      <div className="dc-alert-actions">
                        <button
                          id={`btn-view-details-${activeAlert.id}`}
                          className="btn-primary"
                          style={{ flex: 1 }}
                          onClick={() => onNavigate("reports")}
                        >
                          View Reports
                        </button>
                        <button
                          id={`btn-acknowledge-${activeAlert.id}`}
                          className={`btn-outline${activeAlert.acknowledged ? " acknowledged" : ""}`}
                          style={{ flex: 1 }}
                          onClick={() => handleAck(activeAlert.id)}
                          disabled={activeAlert.acknowledged}
                        >
                          {activeAlert.acknowledged ? "✓ Acknowledged" : "Acknowledge"}
                        </button>
                      </div>

                      {/* Real contextual data from linked disaster */}
                      <div className="dc-context-section">
                        <p className="dc-context-label">Incident Intelligence</p>
                        {activeAlert.disaster_type && (
                          <div className="dc-context-item">
                            <div className="dc-context-icon-wrap">
                              <span className="material-symbols-outlined">{typeIcon(activeAlert.disaster_type)}</span>
                            </div>
                            <div>
                              <p className="dc-context-title">
                                {activeAlert.disaster_type?.charAt(0).toUpperCase() + activeAlert.disaster_type?.slice(1)} Event
                              </p>
                              <p className="dc-context-desc">
                                Severity index: {activeAlert.severity_score != null ? `${Math.round(activeAlert.severity_score * 100)}%` : "N/A"}
                                {activeAlert.latitude != null && ` · Coords: ${activeAlert.latitude?.toFixed(3)}, ${activeAlert.longitude?.toFixed(3)}`}
                              </p>
                            </div>
                          </div>
                        )}
                        {!activeAlert.disaster_type && (
                          <div className="dc-context-item">
                            <div className="dc-context-icon-wrap">
                              <span className="material-symbols-outlined">radar</span>
                            </div>
                            <div>
                              <p className="dc-context-title">Sensor Data</p>
                              <p className="dc-context-desc">Alert ID #{activeAlert.id} — Linked disaster data unavailable.</p>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Escalation probability bar */}
                      <div className="dc-prob-section">
                        <div className="dc-prob-header">
                          <span className="dc-prob-label">Escalation Probability</span>
                          <span className="dc-prob-value" style={{ color: activeAlert.escalation_probability > 80 ? "var(--error)" : "var(--secondary)" }}>
                            {activeAlert.escalation_probability?.toFixed(0)}%
                          </span>
                        </div>
                        <div className="progress-track">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${activeAlert.escalation_probability}%`,
                              background: activeAlert.escalation_probability > 80 ? "var(--error)" : "var(--primary)"
                            }}
                          />
                        </div>
                      </div>

                      {/* Open Tactical Dossier Button */}
                      <button
                        type="button"
                        className="btn-tonal"
                        id="btn-open-dossier"
                        style={{
                          width: "100%",
                          marginTop: "12px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "8px",
                          fontSize: "12.5px"
                        }}
                        onClick={() => {
                          const linked = disasters.find(d => d.id === activeAlert.disaster_id);
                          if (linked) {
                            setDossierIncident(linked);
                          } else {
                            setDossierIncident({
                              id: activeAlert.disaster_id || activeAlert.id,
                              title: activeAlert.title,
                              disaster_type: activeAlert.disaster_type || "hazard",
                              risk_level: activeAlert.level,
                              latitude: activeAlert.latitude || 20.0,
                              longitude: activeAlert.longitude || 78.0,
                              sitrep_summary: activeAlert.description,
                              acknowledged: activeAlert.acknowledged,
                              source_origin: "ALERT_FEED",
                            });
                          }
                        }}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 18 }}>assignment</span>
                        Open Tactical Dossier
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── Slide-out Tactical SITREP Dossier Drawer ── */}
      <SitrepDossierDrawer
        incident={dossierIncident}
        onClose={() => setDossierIncident(null)}
        onAcknowledge={handleIncidentAcknowledged}
      />

      {/* ── New Incident Modal ── */}
      {newIncidentOpen && (
        <div className="modal-overlay" onClick={() => { setNewIncidentOpen(false); setFormError(""); setForm(INITIAL_FORM); }}>
          <div className="modal-card slide-in" onClick={e => e.stopPropagation()} style={{ maxWidth: 500, width: "100%", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 24, color: "var(--primary)" }}>smart_toy</span>
              <h3 className="modal-title" style={{ margin: 0 }}>Report Incident & Run AI Synthesis</h3>
            </div>
            <p style={{ fontSize: "13px", color: "var(--on-surface-variant)", margin: "0 0 4px" }}>
              Inject manual field observations or telemetry. The platform will synthesize a tactical SITREP and place the marker on the live map.
            </p>

            {formError && (
              <div style={{ background: "rgba(176,38,20,0.1)", border: "1px solid var(--primary)", borderRadius: 8, padding: "10px 14px", fontSize: "13px", color: "var(--primary)" }}>
                {formError}
              </div>
            )}

            <form onSubmit={handleNewIncidentSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div className="signin-field">
                <label htmlFor="ni-type">Disaster Classification</label>
                <select
                  id="ni-type"
                  name="disaster_type"
                  className="tech-input"
                  value={form.disaster_type}
                  onChange={handleFormChange}
                >
                  <option value="flood">Flood / Inundation</option>
                  <option value="fire">Wildfire / Urban Fire</option>
                  <option value="earthquake">Earthquake / Seismic</option>
                  <option value="storm">Severe Weather / Storm</option>
                </select>
              </div>

              <div className="signin-field">
                <label htmlFor="ni-title">Incident Title / Observations</label>
                <input
                  id="ni-title"
                  name="title"
                  type="text"
                  className="tech-input"
                  placeholder="e.g. Low-Lying Riverbank Overtopping"
                  value={form.title}
                  onChange={handleFormChange}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="signin-field">
                  <label htmlFor="ni-lat">Latitude</label>
                  <input id="ni-lat" name="latitude" type="number" step="any" className="tech-input" placeholder="e.g. 28.61" value={form.latitude} onChange={handleFormChange} required />
                </div>
                <div className="signin-field">
                  <label htmlFor="ni-lng">Longitude</label>
                  <input id="ni-lng" name="longitude" type="number" step="any" className="tech-input" placeholder="e.g. 77.20" value={form.longitude} onChange={handleFormChange} required />
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="signin-field">
                  <label htmlFor="ni-rainfall">Rainfall (mm/h)</label>
                  <input id="ni-rainfall" name="weather_rainfall" type="number" step="any" min="0" className="tech-input" value={form.weather_rainfall} onChange={handleFormChange} required />
                </div>
                <div className="signin-field">
                  <label htmlFor="ni-wind">Wind Speed (km/h)</label>
                  <input id="ni-wind" name="weather_wind_speed" type="number" step="any" min="0" className="tech-input" value={form.weather_wind_speed} onChange={handleFormChange} required />
                </div>
              </div>

              <div className="signin-field">
                <label htmlFor="ni-social">Citizen Social Signal (0.0 – 1.0)</label>
                <input id="ni-social" name="social_signal_score" type="number" step="0.01" min="0" max="1" className="tech-input" value={form.social_signal_score} onChange={handleFormChange} required />
              </div>

              <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
                <button type="submit" id="btn-submit-incident" className="btn-primary" style={{ flex: 1 }} disabled={submitting}>
                  <span className="material-symbols-outlined">{submitting ? "hourglass_empty" : "radar"}</span>
                  {submitting ? "Synthesizing SITREP..." : "Submit Incident"}
                </button>
                <button
                  type="button"
                  className="btn-outline modal-cancel"
                  style={{ flex: 0 }}
                  onClick={() => { setNewIncidentOpen(false); setFormError(""); setForm(INITIAL_FORM); }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
