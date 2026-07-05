import React, { useState } from "react";
import "./SignIn.css";

export default function SignIn({ onSignIn }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);

  const handleEmail = (e) => {
    e.preventDefault();
    onSignIn({ name: "Dr. Aris Thorne", email: email || "analyst@terra-aura.dev", provider: "email" });
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
              <h1 className="signin-title">Welcome Back</h1>
              <p className="signin-subtitle">Sign in to continue to the Disaster Center</p>
            </div>
          </div>

          <div className="signin-actions">
            <button
              id="btn-google-signin"
              className="btn-oauth"
              onClick={() => onSignIn({ name: "Google User", email: "user@gmail.com", provider: "google" })}
            >
              <svg width="18" height="18" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M47.532 24.552c0-1.636-.147-3.2-.418-4.704H24v8.896h13.218c-.57 3.066-2.304 5.664-4.91 7.406v6.148h7.946c4.648-4.278 7.278-10.578 7.278-17.746z" fill="#4285F4"/>
                <path d="M24 48c6.642 0 12.21-2.2 16.28-5.966l-7.948-6.148c-2.202 1.474-5.016 2.346-8.332 2.346-6.408 0-11.832-4.328-13.772-10.14H2.046v6.35C6.098 42.692 14.46 48 24 48z" fill="#34A853"/>
                <path d="M10.228 28.092c-.492-1.474-.772-3.048-.772-4.672s.28-3.198.772-4.672v-6.35H2.046A23.996 23.996 0 0 0 0 24c0 3.874.928 7.542 2.576 10.774l7.652-6.682z" fill="#FBBC05"/>
                <path d="M24 9.516c3.61 0 6.848 1.24 9.396 3.68l7.046-7.046C36.21 2.2 30.642 0 24 0 14.46 0 6.098 5.308 2.046 13.226l7.652 6.682C11.638 14.096 17.592 9.516 24 9.516z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>

            <button
              id="btn-apple-signin"
              className="btn-oauth"
              onClick={() => onSignIn({ name: "Apple User", email: "user@icloud.com", provider: "apple" })}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/>
              </svg>
              Continue with Apple
            </button>
          </div>

          <div className="signin-divider">
            <div className="divider" />
            <span>or sign in with email</span>
            <div className="divider" />
          </div>

          <form className="signin-form" onSubmit={handleEmail}>
            <div className="signin-field">
              <label htmlFor="signin-email">Institutional Email</label>
              <input
                id="signin-email"
                type="email"
                className="tech-input"
                placeholder="analyst@terra-aura.dev"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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

            <button id="btn-email-signin" type="submit" className="btn-primary signin-submit glow-hover">
              <span className="material-symbols-outlined">login</span>
              Sign In with Email
            </button>
          </form>

          <p className="signin-footer">
            Protected by Terra-Aura Security. Clearance level required.
          </p>
        </div>
      </div>
    </div>
  );
}
