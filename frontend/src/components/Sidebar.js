import React, { useState, useEffect } from "react";
import "./Sidebar.css";

const navItems = [
  { id: "dashboard", icon: "dashboard", label: "Dashboard" },
  { id: "disaster-center", icon: "map", label: "Disaster Center" },
  { id: "analytics", icon: "bar_chart", label: "Analytics" },
  { id: "reports", icon: "description", label: "Reports" },
  { id: "profile", icon: "settings", label: "Settings" },
];

const bottomItems = [
  { id: "system-status", icon: "monitor_heart", label: "System Status" },
  { id: "legal", icon: "gavel", label: "Legal & Support" },
  { id: "logout", icon: "logout", label: "Log Out", danger: true },
];

export default function Sidebar({ active, onNavigate }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  // Prevent background scroll when mobile drawer is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const handleNavClick = (id) => {
    setMobileOpen(false);
    onNavigate(id);
  };

  return (
    <>
      {/* Mobile Hamburger Toggle Button */}
      <button
        type="button"
        className="sidebar-mobile-toggle"
        onClick={() => setMobileOpen(true)}
        aria-label="Open navigation menu"
        id="btn-sidebar-mobile-open"
      >
        <span className="material-symbols-outlined">menu</span>
      </button>

      {/* Backdrop overlay for mobile drawer */}
      {mobileOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Drawer */}
      <aside className={`sidebar${mobileOpen ? " mobile-open" : ""}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <span className="material-symbols-outlined sidebar-brand-icon">landscape</span>
            <div>
              <div className="sidebar-brand-name">Terra-Aura</div>
              <div className="sidebar-brand-sub">Disaster Intel</div>
            </div>
          </div>

          <button
            type="button"
            className="sidebar-mobile-close"
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation menu"
            id="btn-sidebar-mobile-close"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              className={`nav-item${active === item.id ? " active" : ""}`}
              onClick={() => handleNavClick(item.id)}
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
              id={`nav-${item.id}`}
              className={`nav-item${item.danger ? " nav-danger" : ""}${active === item.id ? " active" : ""}`}
              onClick={() => handleNavClick(item.id)}
              aria-label={item.label}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </aside>
    </>
  );
}
