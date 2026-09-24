import React, { useState, useEffect, useRef, useCallback } from "react";
import "./Topbar.css";
import { disastersApi, reportsApi } from "../services/api";
import { useNotifications } from "../context/NotificationContext";

const PAGE_TITLES = {
  dashboard: "Operations Dashboard",
  "disaster-center": "Disaster Center",
  analytics: "Analytics",
  reports: "Reports",
  profile: "Profile Settings",
  legal: "Legal & Support",
  "system-status": "System Status",
  "backend-pending": "Feature In Progress",
  "not-found": "Sector Not Found",
  logout: "",
};

const timeAgo = (isoStr) => {
  if (!isoStr) return "";
  const diff = (Date.now() - new Date(isoStr)) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return new Date(isoStr).toLocaleDateString();
};

export default function Topbar({ user, activePage, onNavigate }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [allData, setAllData] = useState({ disasters: [], reports: [] });
  const searchInputRef = useRef(null);
  const notifRef = useRef(null);

  const { notifications, unreadCount, markRead, markAllRead, clearAll } = useNotifications();

  useEffect(() => {
    const handler = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const openSearch = useCallback(async () => {
    setSearchOpen(true);
    setSearchQuery("");
    setSearchResults([]);
    setTimeout(() => searchInputRef.current?.focus(), 50);
    if (allData.disasters.length === 0) {
      setSearchLoading(true);
      try {
        const [dRes, rRes] = await Promise.all([
          disastersApi.list({ limit: 100, sort_by: "created_at", order: "desc", refresh: true }),
          reportsApi.list({ limit: 100 }),
        ]);
        setAllData({
          disasters: dRes.data.data?.items || [],
          reports: rRes.data.data?.items || [],
        });
      } catch (e) {
        console.error("Search data load failed:", e);
      } finally {
        setSearchLoading(false);
      }
    }
  }, [allData.disasters.length]);

  useEffect(() => {
    if (!searchQuery.trim()) { setSearchResults([]); return; }
    const q = searchQuery.toLowerCase();
    const disasterHits = allData.disasters
      .filter(d => d.disaster_type?.toLowerCase().includes(q) || d.risk_level?.toLowerCase().includes(q))
      .slice(0, 5)
      .map(d => ({
        id: `d-${d.id}`,
        icon: "warning",
        label: `${d.disaster_type?.charAt(0).toUpperCase() + d.disaster_type?.slice(1)} - ${d.risk_level}`,
        sub: `${d.latitude?.toFixed(3)}, ${d.longitude?.toFixed(3)}`,
        badge: d.risk_level?.toLowerCase(),
        page: "disaster-center",
      }));
    const reportHits = allData.reports
      .filter(r => r.type?.toLowerCase().includes(q) || r.location?.toLowerCase().includes(q) || r.risk?.toLowerCase().includes(q))
      .slice(0, 5)
      .map(r => ({
        id: `r-${r.id}`,
        icon: "description",
        label: `${r.type} - ${r.report_code}`,
        sub: r.location,
        badge: r.risk,
        page: "reports",
      }));
    setSearchResults([...disasterHits, ...reportHits]);
  }, [searchQuery, allData]);

  const handleResultClick = (result) => {
    setSearchOpen(false);
    setSearchQuery("");
    onNavigate(result.page);
  };

  return (
    <>
      <header className="topbar">
        <div className="topbar-left">
          <h2 className="topbar-page-title">{PAGE_TITLES[activePage] || activePage}</h2>
        </div>
        <div className="topbar-right">
          <button className="btn-icon" aria-label="Search" id="topbar-btn-search" onClick={openSearch}>
            <span className="material-symbols-outlined">search</span>
          </button>

          <div ref={notifRef} style={{ position: "relative" }}>
            <button
              className="btn-icon topbar-notif-btn"
              aria-label="Notifications"
              id="topbar-btn-notifications"
              onClick={() => { setNotifOpen(o => !o); setDropdownOpen(false); }}
            >
              <span className="material-symbols-outlined">notifications</span>
              {unreadCount > 0 && (
                <span className="topbar-notif-badge">{unreadCount > 9 ? "9+" : unreadCount}</span>
              )}
            </button>

            {notifOpen && (
              <div className="topbar-notif-panel">
                <div className="topbar-notif-header">
                  <span className="topbar-notif-title">Notifications</span>
                  <div style={{ display: "flex", gap: 4 }}>
                    {unreadCount > 0 && (
                      <button className="topbar-notif-action" onClick={markAllRead}>Mark all read</button>
                    )}
                    {notifications.length > 0 && (
                      <button className="topbar-notif-action" onClick={clearAll}>Clear all</button>
                    )}
                  </div>
                </div>
                <div className="topbar-notif-list">
                  {notifications.length === 0 ? (
                    <p className="topbar-notif-empty">No notifications yet.</p>
                  ) : (
                    notifications.map(n => (
                      <div
                        key={n.id}
                        className={`topbar-notif-item${n.read ? " read" : ""}`}
                        onClick={() => markRead(n.id)}
                      >
                        <span className="material-symbols-outlined topbar-notif-icon">{n.icon}</span>
                        <div className="topbar-notif-body">
                          <p className="topbar-notif-item-title">{n.title}</p>
                          {n.message && <p className="topbar-notif-item-msg">{n.message}</p>}
                          <p className="topbar-notif-item-time">{timeAgo(n.timestamp)}</p>
                        </div>
                        {!n.read && <span className="topbar-notif-dot" />}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="topbar-profile-wrap">
            <button
              className="topbar-profile-btn"
              id="topbar-btn-profile"
              onClick={() => { setDropdownOpen(!dropdownOpen); setNotifOpen(false); }}
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
                  { label: "Profile", icon: "person", page: "profile" },
                  { label: "Support", icon: "help", page: "legal" },
                  { label: "Logout", icon: "logout", page: "logout", danger: true },
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

      {searchOpen && (
        <div className="search-overlay" onClick={() => setSearchOpen(false)}>
          <div className="search-modal" onClick={e => e.stopPropagation()}>
            <div className="search-input-wrap">
              <span className="material-symbols-outlined search-modal-icon">search</span>
              <input
                ref={searchInputRef}
                type="text"
                className="search-modal-input"
                placeholder="Search incidents, reports, disaster type, location..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <button className="btn-icon" onClick={() => setSearchOpen(false)} aria-label="Close search">
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>close</span>
              </button>
            </div>
            <div className="search-results">
              {searchLoading && <p className="search-hint">Loading data...</p>}
              {!searchLoading && !searchQuery && (
                <p className="search-hint">Start typing to search across incidents and reports.</p>
              )}
              {!searchLoading && searchQuery && searchResults.length === 0 && (
                <p className="search-hint">No results found for "{searchQuery}".</p>
              )}
              {searchResults.map(r => (
                <button key={r.id} className="search-result-item" onClick={() => handleResultClick(r)}>
                  <span className="material-symbols-outlined search-result-icon">{r.icon}</span>
                  <div className="search-result-text">
                    <span className="search-result-label">{r.label}</span>
                    {r.sub && <span className="search-result-sub">{r.sub}</span>}
                  </div>
                  <span className={`badge badge-${r.badge}`}>{r.badge}</span>
                  <span className="material-symbols-outlined" style={{ fontSize: 16, color: "var(--on-surface-variant)" }}>chevron_right</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
