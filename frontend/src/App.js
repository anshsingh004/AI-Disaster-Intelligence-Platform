import React, { useState, useEffect } from "react";
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

import apiClient from "./services/api";

// Decodes JWT payload properties to restore roles/emails when metadata is missing
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}



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
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    // Bind expired token interceptor to logout the client immediately
    window.onAuthExpired = () => {
      logoutCleanly();
    };

    const verifySession = async () => {
      try {
        // Attempt token refresh on boot to confirm refresh_token cookie viability
        const response = await apiClient.post("/api/v1/auth/refresh");
        const access_token = response.data.data.access_token;
        localStorage.setItem("access_token", access_token);

        const cachedUser = localStorage.getItem("user");
        if (cachedUser) {
          setUser(JSON.parse(cachedUser));
        } else {
          // If user details were missing but token is valid, parse the email/role from access_token
          const payload = parseJwt(access_token);
          const email = payload?.sub || "analyst@terra-aura.dev";
          const role = payload?.role || "ANALYST";
          const fallbackUser = { name: email.split("@")[0], email, role, clearance_level: "Alpha" };
          localStorage.setItem("user", JSON.stringify(fallbackUser));
          setUser(fallbackUser);
        }
      } catch (err) {
        // If refresh fails, clear out expired access metrics
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        setUser(null);
      } finally {
        setInitializing(false);
      }
    };

    verifySession();

    return () => {
      window.onAuthExpired = null;
    };
  }, []);

  const signIn = (userObj) => {
    setUser(userObj);
    setActivePage("dashboard");
  };

  const logoutCleanly = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
    setActivePage("dashboard");
  };

  const logout = async () => {
    try {
      await apiClient.post("/api/v1/auth/logout");
    } catch (e) {
      console.warn("API logout call failed:", e);
    }
    logoutCleanly();
  };

  const navigate = (page) => {
    if (page === "logout") { logout(); return; }
    setActivePage(page);
  };

  // 1. Initializing secure connection status
  if (initializing) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        background: "#0c0b05",
        color: "#f5f1d8",
        gap: "16px",
        fontFamily: "var(--font-manrope, sans-serif)"
      }}>
        <span className="material-symbols-outlined pulse" style={{ fontSize: 48, color: "var(--primary)" }}>
          satellite_alt
        </span>
        <p style={{ fontSize: "14px", fontWeight: "600", letterSpacing: "0.05em", opacity: 0.8 }}>
          Verifying secure EOC session...
        </p>
      </div>
    );
  }

  // 2. Unauthenticated state → show sign in and register page
  if (!user) {
    return <SignIn onSignIn={signIn} />;
  }

  // 3. Signed in → shell layout
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
