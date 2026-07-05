import React, { useState } from "react";
import "./index.css";
import "./App.css";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import SignIn from "./pages/SignIn";
import Dashboard from "./pages/Dashboard";
import DisasterCenter from "./pages/DisasterCenter";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import Legal from "./pages/Legal";
import BackendPending from "./pages/BackendPending";

// Pages that need the sidebar / topbar layout
const SHELL_PAGES = [
  "dashboard",
  "disaster-center",
  "analytics",
  "reports",
  "profile",
  "legal",
  "support",
  "system-status",
  "backend-pending",
];

function renderPage(page, user, navigate, logout) {
  switch (page) {
    case "dashboard":        return <Dashboard        user={user}    onNavigate={navigate} />;
    case "disaster-center":  return <DisasterCenter   user={user}    onNavigate={navigate} />;
    case "analytics":        return <Analytics                       onNavigate={navigate} />;
    case "reports":          return <Reports                         onNavigate={navigate} />;
    case "profile":          return <Profile          user={user}    onNavigate={navigate} onLogout={logout} />;
    case "legal":            return <Legal                           onNavigate={navigate} />;
    case "support":          return <BackendPending                  onNavigate={navigate} />;
    case "system-status":    return <BackendPending                  onNavigate={navigate} />;
    case "backend-pending":  return <BackendPending                  onNavigate={navigate} />;
    default:                 return <BackendPending                  onNavigate={navigate} />;
  }
}

export default function App() {
  const [user, setUser] = useState(null);
  const [activePage, setActivePage] = useState("dashboard");

  const signIn = (userObj) => {
    setUser(userObj);
    setActivePage("dashboard");
  };

  const logout = () => {
    setUser(null);
    setActivePage("dashboard");
  };

  const navigate = (page) => {
    if (page === "logout") { logout(); return; }
    setActivePage(page);
  };

  // Not signed in → show sign in page
  if (!user) {
    return <SignIn onSignIn={signIn} />;
  }

  // Signed in → shell layout
  return (
    <div className="app-shell">
      <Sidebar active={activePage} onNavigate={navigate} />

      <div className="app-main">
        {/* DisasterCenter has its own topbar built in */}
        {activePage !== "disaster-center" && (
          <Topbar user={user} activePage={activePage} onNavigate={navigate} />
        )}

        <div className="app-content">
          {renderPage(activePage, user, navigate, logout)}
        </div>
      </div>
    </div>
  );
}
