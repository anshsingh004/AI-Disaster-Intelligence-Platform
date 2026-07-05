import React from "react";
import "./Sidebar.css";

const navItems = [
  { id: "dashboard", icon: "dashboard", label: "Dashboard" },
  { id: "disaster-center", icon: "map", label: "Disaster Center" },
  { id: "analytics", icon: "bar_chart", label: "Analytics" },
  { id: "reports", icon: "description", label: "Reports" },
  { id: "profile", icon: "settings", label: "Settings" },
];

const bottomItems = [
  { id: "system-status", icon: "security", label: "System Status" },
  { id: "support", icon: "help_center", label: "Support" },
  { id: "legal", icon: "gavel", label: "Legal" },
  { id: "logout", icon: "logout", label: "Log Out", danger: true },
];

export default function Sidebar({ active, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="material-symbols-outlined sidebar-brand-icon">landscape</span>
        <div>
          <div className="sidebar-brand-name">Terra-Aura</div>
          <div className="sidebar-brand-sub">Disaster Intel</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item${active === item.id ? " active" : ""}`}
            onClick={() => onNavigate(item.id)}
            aria-label={item.label}
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-spacer" />

      <div className="sidebar-bottom">
        <div className="divider" style={{ marginBottom: 8 }} />
        {bottomItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item${item.danger ? " nav-danger" : ""}${active === item.id ? " active" : ""}`}
            onClick={() => onNavigate(item.id)}
            aria-label={item.label}
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}
