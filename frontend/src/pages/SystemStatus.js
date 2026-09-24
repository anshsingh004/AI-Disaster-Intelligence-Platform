import React, { useState, useEffect, useCallback } from "react";
import "./SystemStatus.css";
import { systemApi } from "../services/api";

const REFRESH_INTERVAL = 30000; // 30s auto-refresh

const formatUptime = (seconds) => {
  if (!seconds && seconds !== 0) return "—";
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  return `${m}m ${s}s`;
};

const StatusBadge = ({ value }) => {
  const cls = value?.toLowerCase?.() || "offline";
  return <span className={`ss-card-status ${cls}`}>{value || "unknown"}</span>;
};

const ServiceCard = ({ icon, label, value, statusKey }) => {
  const iconClass = ["online","connected","active","healthy"].includes((statusKey || value || "").toLowerCase())
    ? "online"
    : ["offline","disconnected"].includes((statusKey || value || "").toLowerCase())
    ? "offline"
    : "warning";

  return (
    <div className="ss-card">
      <div className={`ss-card-icon ${iconClass}`}>
        <span className="material-symbols-outlined">{icon}</span>
      </div>
      <div className="ss-card-body">
        <p className="ss-card-label">{label}</p>
        <StatusBadge value={value} />
      </div>
    </div>
  );
};

export default function SystemStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [spinning, setSpinning] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async (manual = false) => {
    if (manual) setSpinning(true);
    try {
      const res = await systemApi.status();
      setStatus(res.data);
      setError(null);
    } catch (e) {
      setError("Could not reach backend. Some metrics may be unavailable.");
      // Set degraded status
      setStatus(prev => prev || {
        backend_api: "offline",
        database: "unknown",
        redis: "unknown",
        auth_service: "unknown",
        ai_engine: "unknown",
        cache: "unknown",
        api_latency_ms: null,
        db_latency_ms: null,
        redis_latency_ms: null,
        uptime_seconds: null,
        build_version: "—",
        last_health_check: new Date().toISOString(),
        docker_health: "unknown",
      });
    } finally {
      setLoading(false);
      if (manual) setTimeout(() => setSpinning(false), 600);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(() => fetchStatus(), REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const latencyClass = (ms) => {
    if (ms === null || ms === undefined) return "";
    if (ms < 20) return "";
    if (ms < 100) return "slow";
    return "critical";
  };

  const latencyWidth = (ms) => {
    if (ms === null || ms === undefined) return "0%";
    return `${Math.min(100, (ms / 200) * 100)}%`;
  };

  if (loading) {
    return (
      <div className="ss-root fade-in">
        <div className="ss-loading">
          <span className="material-symbols-outlined pulse">monitor_heart</span>
          Running diagnostics...
        </div>
      </div>
    );
  }

  const s = status || {};

  return (
    <div className="ss-root fade-in">
      <header className="ss-header">
        <div>
          <h1 className="ss-title">System Status</h1>
          <p className="ss-sub">Real-time health diagnostics for all Terra-Aura platform services</p>
          {error && (
            <p style={{ fontSize: 12, color: "var(--error)", marginTop: 4 }}>
              ⚠ {error}
            </p>
          )}
        </div>
        <button
          className={`ss-refresh-btn${spinning ? " spinning" : ""}`}
          onClick={() => fetchStatus(true)}
          id="btn-system-refresh"
        >
          <span className="material-symbols-outlined">refresh</span>
          Refresh
        </button>
      </header>

      {/* Service Status Cards */}
      <div className="ss-grid">
        <ServiceCard icon="cloud_done"         label="Backend API"    value={s.backend_api}    statusKey={s.backend_api} />
        <ServiceCard icon="database"           label="PostgreSQL DB"  value={s.database}       statusKey={s.database} />
        <ServiceCard icon="memory"             label="Redis Cache"    value={s.redis}          statusKey={s.redis} />
        <ServiceCard icon="lock"               label="Auth Service"   value={s.auth_service}   statusKey={s.auth_service} />
        <ServiceCard icon="smart_toy"          label="AI Engine"      value={s.ai_engine}      statusKey={s.ai_engine} />
        <ServiceCard icon="cached"             label="Cache Layer"    value={s.cache}          statusKey={s.cache} />
        <ServiceCard icon="deployed_code"      label="Docker Health"  value={s.docker_health}  statusKey={s.docker_health} />
      </div>

      {/* Metrics Grid */}
      <div className="ss-meta-grid">
        {/* API Latency */}
        <div className="ss-meta-card">
          <p className="ss-meta-label">API Latency</p>
          <p className="ss-meta-value">
            {s.api_latency_ms !== null && s.api_latency_ms !== undefined
              ? <>{s.api_latency_ms}<span className="ss-meta-unit"> ms</span></>
              : "—"}
          </p>
          <div className="ss-latency-bar">
            <div
              className={`ss-latency-fill ${latencyClass(s.api_latency_ms)}`}
              style={{ width: latencyWidth(s.api_latency_ms) }}
            />
          </div>
        </div>

        {/* DB Latency */}
        <div className="ss-meta-card">
          <p className="ss-meta-label">DB Query Latency</p>
          <p className="ss-meta-value">
            {s.db_latency_ms !== null && s.db_latency_ms !== undefined
              ? <>{s.db_latency_ms}<span className="ss-meta-unit"> ms</span></>
              : "—"}
          </p>
          <div className="ss-latency-bar">
            <div
              className={`ss-latency-fill ${latencyClass(s.db_latency_ms)}`}
              style={{ width: latencyWidth(s.db_latency_ms) }}
            />
          </div>
        </div>

        {/* Redis Latency */}
        <div className="ss-meta-card">
          <p className="ss-meta-label">Redis Latency</p>
          <p className="ss-meta-value">
            {s.redis_latency_ms !== null && s.redis_latency_ms !== undefined
              ? <>{s.redis_latency_ms}<span className="ss-meta-unit"> ms</span></>
              : "—"}
          </p>
          <div className="ss-latency-bar">
            <div
              className={`ss-latency-fill ${latencyClass(s.redis_latency_ms)}`}
              style={{ width: latencyWidth(s.redis_latency_ms) }}
            />
          </div>
        </div>

        {/* Uptime */}
        <div className="ss-meta-card">
          <p className="ss-meta-label">Backend Uptime</p>
          <p className="ss-meta-value" style={{ fontSize: 16 }}>
            {formatUptime(s.uptime_seconds)}
          </p>
        </div>

        {/* Build Version */}
        <div className="ss-meta-card">
          <p className="ss-meta-label">Build Version</p>
          <p className="ss-meta-value">v{s.build_version || "—"}</p>
        </div>

        {/* Last Check */}
        <div className="ss-meta-card">
          <p className="ss-meta-label">Last Health Check</p>
          <p className="ss-meta-value" style={{ fontSize: 13 }}>
            {s.last_health_check
              ? new Date(s.last_health_check).toLocaleTimeString()
              : "—"}
          </p>
          <p className="ss-meta-label" style={{ marginTop: 4 }}>
            {s.last_health_check ? new Date(s.last_health_check).toLocaleDateString() : ""}
          </p>
        </div>
      </div>

      <div className="ss-footer">
        Auto-refreshes every 30 seconds · Terra-Aura Intelligence Platform · Build {s.build_version || "1.0.0"}
      </div>
    </div>
  );
}

