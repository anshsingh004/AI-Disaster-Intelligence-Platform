import React, { useState } from "react";
import "./Profile.css";

export default function Profile({ user, onNavigate, onLogout }) {
  const [alerts, setAlerts] = useState({
    sms: true,
    deployment: false,
    digest: true,
    maintenance: false,
  });
  const [role, setRole] = useState("Lead Geospatial Analyst");
  const [saved, setSaved] = useState(false);

  const toggleAlert = (key) =>
    setAlerts((prev) => ({ ...prev, [key]: !prev[key] }));

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const ALERT_ITEMS = [
    { key: "sms",         label: "Critical Event SMS",   sub: "Immediate deployment pings" },
    { key: "deployment",  label: "Immediate deployment pings", sub: "Field alerts for rapid response" },
    { key: "digest",      label: "Daily Intel Digest",   sub: "Sector activity summary" },
    { key: "maintenance", label: "System Maintenance",   sub: "Platform updates" },
  ];

  return (
    <div className="profile-root fade-in">
      <header className="profile-header">
        <div className="profile-avatar-wrap">
          <img
            src="https://ui-avatars.com/api/?name=Dr+Aris+Thorne&background=ffdad4&color=b02614&size=96&bold=true&font-size=0.35"
            alt="Profile"
            className="profile-avatar"
          />
          <div className="profile-avatar-edit btn-icon" aria-label="Edit photo" onClick={() => onNavigate("backend-pending")}>
            <span className="material-symbols-outlined">photo_camera</span>
          </div>
        </div>
        <div className="profile-identity">
          <h1 className="profile-name">{user?.name || "Dr. Aris Thorne"}</h1>
          <p className="profile-role-line">Lead Geospatial Analyst, Sector 4</p>
          <span className="profile-clearance-chip">
            <span className="material-symbols-outlined" style={{fontSize:13}}>shield</span>
            Clearance Level: Alpha
          </span>
        </div>
      </header>

      <div className="profile-sections">
        {/* Personal Info */}
        <section className="profile-card card-lift">
          <div className="profile-section-header">
            <span className="material-symbols-outlined profile-section-icon">person</span>
            <h2 className="profile-section-title">Personal Information</h2>
          </div>
          <div className="profile-fields">
            <div className="profile-field">
              <label>Full Name</label>
              <input className="tech-input" defaultValue={user?.name || "Dr. Aris Thorne"} />
            </div>
            <div className="profile-field">
              <label>Institutional Email</label>
              <input className="tech-input" defaultValue={user?.email || "a.thorne@terra-aura.dev"} />
            </div>
            <div className="profile-field">
              <label>Operational Role</label>
              <select className="tech-input" value={role} onChange={(e) => setRole(e.target.value)}>
                <option>Lead Geospatial Analyst</option>
                <option>Field Operative Coordinator</option>
                <option>Logistics Director</option>
                <option>Environmental Scientist</option>
              </select>
            </div>
            <div className="profile-field profile-field-full">
              <label>Background & Specialization</label>
              <textarea
                className="tech-input profile-bio"
                defaultValue="12 years specializing in tectonic shift prediction and high-altitude atmospheric disturbance modeling. Secondary expertise in rapid deployment logistics."
                rows={3}
              />
            </div>
          </div>
          <div className="profile-card-footer">
            <button
              id="btn-save-profile"
              className={`btn-primary${saved ? " btn-saved" : ""}`}
              onClick={handleSave}
            >
              {saved ? (
                <><span className="material-symbols-outlined">check</span> Saved!</>
              ) : (
                <><span className="material-symbols-outlined">save</span> Save Changes</>
              )}
            </button>
          </div>
        </section>

        {/* Alert Preferences */}
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

        {/* Session */}
        <section className="profile-card card-lift profile-session-card">
          <div className="profile-section-header">
            <span className="material-symbols-outlined profile-section-icon">security</span>
            <h2 className="profile-section-title">Session</h2>
          </div>
          <p className="profile-session-note">
            Ensure all unsaved reports are committed before exiting.
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
