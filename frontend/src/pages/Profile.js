import React, { useState } from "react";
import "./Profile.css";
import { meApi } from "../services/api";

const ALERT_ITEMS = [
  { key: "sms",         label: "Critical Event SMS",        sub: "Immediate deployment pings" },
  { key: "deployment",  label: "Immediate Deployment Pings", sub: "Field alerts for rapid response" },
  { key: "digest",      label: "Daily Intel Digest",         sub: "Sector activity summary" },
  { key: "maintenance", label: "System Maintenance",          sub: "Platform updates" },
];

const ROLE_LABELS = {
  ADMINISTRATOR: "System Administrator",
  EOC_LEAD: "EOC Lead",
  ANALYST: "Lead Analyst",
  FIELD_OPERATIVE: "Field Operative",
};

export default function Profile({ user, onNavigate, onLogout, onUserUpdate }) {
  // Alert preferences are local — no backend API for them yet
  const [alerts, setAlerts] = useState({ sms: true, deployment: false, digest: true, maintenance: false });

  // Editable fields
  const [name, setName] = useState(user?.name || "");
  const [saving, setSaving] = useState(false);
  const [saveState, setSaveState] = useState("idle"); // "idle" | "saved" | "error"

  const toggleAlert = (key) => setAlerts(prev => ({ ...prev, [key]: !prev[key] }));

  // ── Save profile changes ───────────────────────────────────────────────────

  const handleSave = async () => {
    if (!name.trim() || name.trim().length < 2) return;
    setSaving(true);
    setSaveState("idle");
    try {
      const res = await meApi.update({ name: name.trim() });
      const updatedUser = res.data.data;
      // Propagate updated user to App.js session state
      if (onUserUpdate) onUserUpdate(updatedUser);
      setSaveState("saved");
      setTimeout(() => setSaveState("idle"), 2500);
    } catch (err) {
      console.error("Profile update failed:", err);
      setSaveState("error");
      setTimeout(() => setSaveState("idle"), 3000);
    } finally {
      setSaving(false);
    }
  };

  // ── Avatar URL from real user name ────────────────────────────────────────

  const avatarUrl = user?.name
    ? `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=ffdad4&color=b02614&size=96&bold=true&font-size=0.35`
    : "https://ui-avatars.com/api/?name=User&background=ffdad4&color=b02614&size=96";

  const roleLabel = ROLE_LABELS[user?.role] || user?.role || "Analyst";
  const clearance = user?.clearance_level || "Alpha";

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="profile-root fade-in">
      <header className="profile-header">
        <div className="profile-avatar-wrap">
          <img src={avatarUrl} alt="Profile" className="profile-avatar" />
          <div className="profile-avatar-edit btn-icon" aria-label="Edit photo" onClick={() => {}}>
            <span className="material-symbols-outlined">photo_camera</span>
          </div>
        </div>
        <div className="profile-identity">
          <h1 className="profile-name">{user?.name || "User"}</h1>
          <p className="profile-role-line">{roleLabel}</p>
          <span className="profile-clearance-chip">
            <span className="material-symbols-outlined" style={{ fontSize: 13 }}>shield</span>
            Clearance Level: {clearance}
          </span>
        </div>
      </header>

      <div className="profile-sections">
        {/* ── Personal Info ── */}
        <section className="profile-card card-lift">
          <div className="profile-section-header">
            <span className="material-symbols-outlined profile-section-icon">person</span>
            <h2 className="profile-section-title">Personal Information</h2>
          </div>
          <div className="profile-fields">
            <div className="profile-field">
              <label htmlFor="profile-name">Full Name</label>
              <input
                id="profile-name"
                className="tech-input"
                value={name}
                onChange={e => { setName(e.target.value); setSaveState("idle"); }}
                placeholder="Your name"
              />
            </div>
            <div className="profile-field">
              <label htmlFor="profile-email">Institutional Email</label>
              <input
                id="profile-email"
                className="tech-input"
                value={user?.email || ""}
                readOnly
                title="Email cannot be changed here"
                style={{ opacity: 0.7, cursor: "not-allowed" }}
              />
            </div>
            <div className="profile-field">
              <label>Operational Role</label>
              <input
                className="tech-input"
                value={roleLabel}
                readOnly
                title="Role is RBAC-controlled and cannot be self-assigned"
                style={{ opacity: 0.7, cursor: "not-allowed" }}
              />
            </div>
            <div className="profile-field profile-field-full">
              <label>Security Clearance</label>
              <input
                className="tech-input"
                value={clearance}
                readOnly
                title="Clearance level is RBAC-controlled"
                style={{ opacity: 0.7, cursor: "not-allowed" }}
              />
            </div>
          </div>

          {saveState === "error" && (
            <p style={{ fontSize: "13px", color: "var(--error)", padding: "0 0 4px", margin: 0 }}>
              Failed to save changes. Please try again.
            </p>
          )}

          <div className="profile-card-footer">
            <button
              id="btn-save-profile"
              className={`btn-primary${saveState === "saved" ? " btn-saved" : ""}`}
              onClick={handleSave}
              disabled={saving || name.trim().length < 2}
            >
              {saveState === "saved" ? (
                <><span className="material-symbols-outlined">check</span> Saved!</>
              ) : saving ? (
                <><span className="material-symbols-outlined">hourglass_empty</span> Saving...</>
              ) : (
                <><span className="material-symbols-outlined">save</span> Save Changes</>
              )}
            </button>
          </div>
        </section>

        {/* ── Alert Preferences (local UX preferences, no backend yet) ── */}
        <section className="profile-card card-lift">
          <div className="profile-section-header">
            <span className="material-symbols-outlined profile-section-icon">tune</span>
            <h2 className="profile-section-title">Alert Preferences</h2>
          </div>
          <div className="profile-alert-list">
            {ALERT_ITEMS.map((item) => (
              <div key={item.key} className="profile-alert-row">
                <div>
                  <p className="profile-alert-label">{item.label}</p>
                  <p className="profile-alert-sub">{item.sub}</p>
                </div>
                <label className="toggle" aria-label={item.label}>
                  <input
                    type="checkbox"
                    id={`toggle-${item.key}`}
                    checked={alerts[item.key]}
                    onChange={() => toggleAlert(item.key)}
                  />
                  <span className="toggle-slider" />
                </label>
              </div>
            ))}
          </div>
        </section>

        {/* ── Session ── */}
        <section className="profile-card card-lift profile-session-card">
          <div className="profile-section-header">
            <span className="material-symbols-outlined profile-section-icon">security</span>
            <h2 className="profile-section-title">Session</h2>
          </div>
          <p className="profile-session-note">
            Ensure all unsaved reports are committed before exiting. Your session is protected by a 15-minute access token with a 7-day refresh cycle.
          </p>
          <button
            id="btn-terminate-session"
            className="btn-danger"
            onClick={() => { onLogout(); }}
          >
            <span className="material-symbols-outlined">power_settings_new</span>
            Terminate Session
          </button>
        </section>
      </div>
    </div>
  );
}
