import React, { useState } from "react";
import "./SignIn.css";
import apiClient from "../services/api";

export default function SignIn({ onSignIn }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("ANALYST");
  const [clearance, setClearance] = useState("Alpha");
  
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    if (!email || !password || (isRegister && !name)) {
      setError("Please fill out all required fields.");
      setLoading(false);
      return;
    }

    try {
      if (isRegister) {
        // Register flow
        const payload = {
          name,
          email,
          password,
          role,
          clearance_level: clearance,
        };
        await apiClient.post("/api/v1/auth/register", payload);
        
        // Transition to login state upon successful registration
        setSuccess("Registration successful! Please sign in using your credentials.");
        setIsRegister(false);
        setPassword("");
      } else {
        // Login flow
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const res = await apiClient.post("/api/v1/auth/login", formData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });
        
        const { user, access_token } = res.data.data;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("user", JSON.stringify(user));
        
        onSignIn(user);
      }
    } catch (err) {
      const errMsg = err.response?.data?.detail || "An unexpected communication error occurred.";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin-root">
      {/* Left decorative panel */}
      <div className="signin-left" aria-hidden="true">
        <div className="signin-map-overlay" />
        <div className="signin-left-content">
          <div className="signin-logo-wrap">
            <span className="material-symbols-outlined signin-globe-icon">public</span>
          </div>
          <div className="signin-tagline">
            <h2>Real-Time Disaster Intelligence</h2>
            <p>AI-powered monitoring, predictive analytics, and global incident response coordination.</p>
          </div>
          <div className="signin-stats">
            <div className="signin-stat">
              <span className="signin-stat-num">1,247</span>
              <span className="signin-stat-label">Active Monitors</span>
            </div>
            <div className="signin-stat">
              <span className="signin-stat-num">94%</span>
              <span className="signin-stat-label">AI Accuracy</span>
            </div>
            <div className="signin-stat">
              <span className="signin-stat-num">89</span>
              <span className="signin-stat-label">Countries</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="signin-right">
        <div className="signin-form-card fade-in">
          <div className="signin-header">
            <div className="signin-avatar">
              <span className="material-symbols-outlined">satellite_alt</span>
            </div>
            <div>
              <p className="signin-eyebrow">TERRA-AURA INTELLIGENCE</p>
              <h1 className="signin-title">
                {isRegister ? "Create Account" : "Welcome Back"}
              </h1>
              <p className="signin-subtitle">
                {isRegister 
                  ? "Register your credentials to register access request" 
                  : "Sign in to continue to the Disaster Center"}
              </p>
            </div>
          </div>

          {/* Feedback Messages */}
          {error && (
            <div style={{
              padding: "12px 16px",
              background: "rgba(176,38,20,0.1)",
              border: "1.5px solid var(--primary)",
              color: "var(--primary)",
              borderRadius: "8px",
              fontSize: "13px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              lineHeight: "1.4"
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>error</span>
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div style={{
              padding: "12px 16px",
              background: "rgba(52,168,83,0.1)",
              border: "1.5px solid #34A853",
              color: "#34A853",
              borderRadius: "8px",
              fontSize: "13px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              lineHeight: "1.4"
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>check_circle</span>
              <span>{success}</span>
            </div>
          )}

          <form className="signin-form" onSubmit={handleSubmit}>
            {isRegister && (
              <div className="signin-field">
                <label htmlFor="signin-name">Full Name</label>
                <input
                  id="signin-name"
                  type="text"
                  className="tech-input"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={loading}
                />
              </div>
            )}
            
            <div className="signin-field">
              <label htmlFor="signin-email">Institutional Email</label>
              <input
                id="signin-email"
                type="email"
                className="tech-input"
                placeholder="analyst@terra-aura.dev"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </div>
            
            <div className="signin-field">
              <label htmlFor="signin-password">Password</label>
              <div className="input-wrap">
                <input
                  id="signin-password"
                  type={showPass ? "text" : "password"}
                  className="tech-input"
                  placeholder="••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                />
                <button
                  type="button"
                  className="input-eye btn-icon"
                  onClick={() => setShowPass(!showPass)}
                  aria-label="Toggle password"
                >
                  <span className="material-symbols-outlined">{showPass ? "visibility_off" : "visibility"}</span>
                </button>
              </div>
            </div>

            {isRegister && (
              <>
                <div className="signin-field">
                  <label htmlFor="signin-role">Operational Role</label>
                  <select
                    id="signin-role"
                    className="tech-input"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    disabled={loading}
                    style={{ background: "var(--surface-container-low)", color: "var(--on-surface)" }}
                  >
                    <option value="ANALYST">ANALYST</option>
                    <option value="EOC_LEAD">EOC_LEAD</option>
                    <option value="ADMINISTRATOR">ADMINISTRATOR</option>
                  </select>
                </div>
                
                <div className="signin-field">
                  <label htmlFor="signin-clearance">Clearance Level</label>
                  <select
                    id="signin-clearance"
                    className="tech-input"
                    value={clearance}
                    onChange={(e) => setClearance(e.target.value)}
                    disabled={loading}
                    style={{ background: "var(--surface-container-low)", color: "var(--on-surface)" }}
                  >
                    <option value="Alpha">Alpha</option>
                    <option value="Beta">Beta</option>
                    <option value="Omega">Omega</option>
                  </select>
                </div>
              </>
            )}

            <button 
              id={isRegister ? "btn-email-register" : "btn-email-signin"} 
              type="submit" 
              className="btn-primary signin-submit glow-hover"
              disabled={loading}
            >
              <span className="material-symbols-outlined">
                {isRegister ? "person_add" : "login"}
              </span>
              {loading ? "Processing..." : isRegister ? "Create Request Account" : "Sign In with Email"}
            </button>
          </form>

          {/* Toggle link between login and register */}
          <p className="signin-toggle-text" style={{ textAlign: "center", fontSize: "13.5px", color: "var(--on-surface-variant)" }}>
            {isRegister ? "Already registered?" : "Don't have an account?"}{" "}
            <button
              type="button"
              style={{ background: "none", border: "none", padding: 0, color: "var(--primary)", fontWeight: "bold", cursor: "pointer", textDecoration: "underline", font: "inherit" }}
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
                setSuccess("");
              }}
            >
              {isRegister ? "Sign In" : "Register"}
            </button>
          </p>

          <p className="signin-footer">
            Protected by Terra-Aura Security. Clearance level required.
          </p>
        </div>
      </div>
    </div>
  );
}
