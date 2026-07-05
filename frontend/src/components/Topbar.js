import React, { useState } from "react";
import "./Topbar.css";

const PAGE_TITLES = {
  dashboard: "Operations Dashboard",
  "disaster-center": "Disaster Center",
  analytics: "Analytics",
  reports: "Reports",
  profile: "Profile Settings",
  legal: "Legal & Support",
  support: "Support",
  "system-status": "System Status",
  "backend-pending": "Feature In Progress",
  logout: "",
};

export default function Topbar({ user, activePage, onNavigate }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h2 className="topbar-page-title">{PAGE_TITLES[activePage] || activePage}</h2>
      </div>

      <div className="topbar-right">
        <button
          className="btn-icon"
          aria-label="Search"
          id="topbar-btn-search"
          onClick={() => onNavigate("backend-pending")}
        >
          <span className="material-symbols-outlined">search</span>
        </button>

        <button
          className="btn-icon topbar-notif-btn"
          aria-label="Notifications"
          id="topbar-btn-notifications"
          onClick={() => onNavigate("backend-pending")}
        >
          <span className="material-symbols-outlined">notifications</span>
          <span className="topbar-notif-badge">3</span>
        </button>

        {/* Profile dropdown */}
        <div className="topbar-profile-wrap">
          <button
            className="topbar-profile-btn"
            id="topbar-btn-profile"
            onClick={() => setDropdownOpen(!dropdownOpen)}
            aria-label="User menu"
          >
            <img
              src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || "User")}&background=ffdad4&color=b02614&size=40&bold=true&font-size=0.35`}
              alt="Profile"
              className="topbar-avatar"
            />
            <div className="topbar-user-info">
              <span className="topbar-user-name">{user?.name || "Analyst"}</span>
              <span className="topbar-user-role">Clearance: Alpha</span>
            </div>
            <span className="material-symbols-outlined topbar-chevron">
              {dropdownOpen ? "expand_less" : "expand_more"}
            </span>
          </button>

          {dropdownOpen && (
            <div className="topbar-dropdown">
              {[
                { label: "Profile",  icon: "person",   page: "profile" },
                { label: "Support",  icon: "help",     page: "support" },
                { label: "Logout",   icon: "logout",   page: "logout", danger: true },
              ].map((item) => (
                <button
                  key={item.label}
                  id={`topbar-dropdown-${item.label.toLowerCase()}`}
                  className={`topbar-dropdown-item${item.danger ? " topbar-dropdown-danger" : ""}`}
                  onClick={() => { setDropdownOpen(false); onNavigate(item.page); }}
                >
                  <span className="material-symbols-outlined">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
