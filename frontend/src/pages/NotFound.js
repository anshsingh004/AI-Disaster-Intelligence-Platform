import React from "react";
import "./NotFound.css";
import useDocumentTitle from "../hooks/useDocumentTitle";

export default function NotFound({ onNavigate }) {
  useDocumentTitle("404 - Sector Not Found | Terra-Aura");

  return (
    <div className="notfound-root fade-in">
      <div className="notfound-grid-bg" />
      <div className="notfound-card">
        <div className="notfound-radar">
          <span className="material-symbols-outlined notfound-radar-icon">radar</span>
        </div>
        <span className="notfound-code">ERROR // CODE 404</span>
        <h1 className="notfound-title">404 — SECTOR NOT FOUND</h1>
        <p className="notfound-desc">
          The requested coordinate, intelligence sector, or tactical dashboard does not exist in the active registry.
          Please re-align your telemetry to an established operational sector.
        </p>
        <div className="notfound-actions">
          <button
            className="btn-primary notfound-btn"
            onClick={() => onNavigate("dashboard")}
          >
            <span className="material-symbols-outlined">dashboard</span>
            Return to Dashboard
          </button>
          <button
            className="btn-outline notfound-btn"
            style={{ color: "#f5f1d8", borderColor: "rgba(245, 241, 216, 0.3)" }}
            onClick={() => onNavigate("disaster-center")}
          >
            <span className="material-symbols-outlined">map</span>
            Disaster Center
          </button>
        </div>
      </div>
    </div>
  );
}
