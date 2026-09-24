import React, { useState } from "react";
import "./SitrepDossierDrawer.css";
import { disastersApi } from "../services/api";

export default function SitrepDossierDrawer({ incident, onClose, onAcknowledge }) {
  const [acking, setAcking] = useState(false);
  const [acknowledged, setAcknowledged] = useState(incident?.acknowledged || false);

  if (!incident) return null;

  const handleAcknowledge = async () => {
    if (acknowledged || acking) return;
    setAcking(true);
    try {
      await disastersApi.acknowledge(incident.id);
      setAcknowledged(true);
      if (onAcknowledge) {
        onAcknowledge(incident.id);
      }
    } catch (err) {
      console.error("Failed to acknowledge disaster:", err);
    } finally {
      setAcking(false);
    }
  };

  const riskLevel = (incident.risk_level || "MEDIUM").toUpperCase();
  const badgeClass = `badge badge-${riskLevel.toLowerCase()}`;
  const actions = Array.isArray(incident.recommended_actions)
    ? incident.recommended_actions
    : incident.recommended_actions
      ? [String(incident.recommended_actions)]
      : [
          "Deploy immediate tactical response units to coordinates",
          "Establish continuous telemetry polling frequency",
          "Coordinate with municipal civil protection assets"
        ];

  const telemetry = incident.raw_telemetry || {};
  const isUSGS = incident.source_origin === "USGS";
  const provenance = isUSGS
    ? "Ingested via Live USGS Feeds · Evaluated via Gemini SITREP Engine"
    : incident.source_origin === "SENSOR_NETWORK"
      ? "Synthesized by Gemini 2.5 Flash from Multi-Modal Sensor Mesh"
      : "Synthesized via Tactical Operational Rules & Intelligence Engine";

  return (
    <div className="dossier-drawer-overlay" onClick={onClose}>
      <div className="dossier-drawer" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="dossier-header">
          <div className="dossier-header-left">
            <div className="dossier-meta-chips">
              <span className={badgeClass}>{riskLevel} Threat</span>
              <span className="dossier-origin-chip">{incident.source_origin || "MANUAL"}</span>
              {acknowledged ? (
                <span className="badge badge-low" style={{ background: "rgba(5, 150, 105, 0.2)", color: "#34d399" }}>
                  ✓ Acknowledged
                </span>
              ) : (
                <span className="badge badge-medium" style={{ background: "rgba(217, 119, 6, 0.2)", color: "#fbbf24" }}>
                  Pending Review
                </span>
              )}
            </div>
            <h2 className="dossier-title">
              {incident.title || `${incident.disaster_type?.toUpperCase()} Incident #${incident.id}`}
            </h2>
          </div>
          <button
            type="button"
            className="dossier-close-btn"
            onClick={onClose}
            aria-label="Close dossier"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="dossier-body">
          {/* AI Provenance Tag */}
          <div className="dossier-ai-provenance">
            <span className="material-symbols-outlined">psychology</span>
            <span>{provenance}</span>
          </div>

          {/* Executive Summary */}
          <div className="dossier-section">
            <span className="dossier-section-title">
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>feed</span>
              Executive Tactical Summary
            </span>
            <p className="dossier-section-content">
              {incident.sitrep_summary ||
                `Tactical assessment for ${incident.disaster_type?.toUpperCase()} incident indicates ${riskLevel} operational risk level at coordinates ${incident.latitude?.toFixed(4)}, ${incident.longitude?.toFixed(4)}. Emergency operations staff should proceed with targeted sector directives.`}
            </p>
          </div>

          {/* Telemetry Breakdown */}
          <div className="dossier-section">
            <span className="dossier-section-title">
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>sensors</span>
              Sensor Telemetry Matrix
            </span>
            <div className="dossier-telemetry-grid">
              <div className="telemetry-tile">
                <span className="telemetry-label">Latitude / Longitude</span>
                <span className="telemetry-value">
                  {incident.latitude?.toFixed(3)}°, {incident.longitude?.toFixed(3)}°
                </span>
              </div>
              <div className="telemetry-tile">
                <span className="telemetry-label">Incident Type</span>
                <span className="telemetry-value" style={{ textTransform: "capitalize" }}>
                  {incident.disaster_type || "Hazard"}
                </span>
              </div>
              {telemetry.magnitude != null && (
                <div className="telemetry-tile">
                  <span className="telemetry-label">Seismic Magnitude</span>
                  <span className="telemetry-value">M {telemetry.magnitude}</span>
                </div>
              )}
              {telemetry.depth_km != null && (
                <div className="telemetry-tile">
                  <span className="telemetry-label">Focal Depth</span>
                  <span className="telemetry-value">{telemetry.depth_km} km</span>
                </div>
              )}
              {telemetry.precipitation != null && (
                <div className="telemetry-tile">
                  <span className="telemetry-label">Precipitation Rate</span>
                  <span className="telemetry-value">{telemetry.precipitation} mm/h</span>
                </div>
              )}
              {telemetry.wind_speed_10m != null && (
                <div className="telemetry-tile">
                  <span className="telemetry-label">Wind Speed</span>
                  <span className="telemetry-value">{telemetry.wind_speed_10m} km/h</span>
                </div>
              )}
            </div>
          </div>

          {/* Recommended Actions */}
          <div className="dossier-section">
            <span className="dossier-section-title">
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>checklist</span>
              Recommended Tactical Actions
            </span>
            <ul className="dossier-actions-list">
              {actions.map((act, idx) => (
                <li key={idx} className="dossier-action-item">
                  <span className="material-symbols-outlined">check_circle</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="dossier-footer">
          <button
            type="button"
            className="btn-outline"
            onClick={onClose}
          >
            Close
          </button>
          <button
            type="button"
            id="btn-dossier-ack"
            className={`btn-primary${acknowledged ? " acknowledged" : ""}`}
            onClick={handleAcknowledge}
            disabled={acknowledged || acking}
          >
            <span className="material-symbols-outlined">
              {acknowledged ? "verified" : acking ? "hourglass_empty" : "check"}
            </span>
            {acknowledged ? "Incident Acknowledged" : acking ? "Acknowledging..." : "Acknowledge Incident"}
          </button>
        </div>
      </div>
    </div>
  );
}
