import axios from "axios";

// ─────────────────────────────────────────────────────────────────────────────
// Base client configuration
// ─────────────────────────────────────────────────────────────────────────────

const getApiBaseUrl = () => {
  if (typeof window !== "undefined") {
    if (window.location.hostname === "localhost") {
      return "http://localhost:8000";
    }
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return "http://localhost:8000";
};

export const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Required to transmit secure HTTP-only cookies
});

// ─────────────────────────────────────────────────────────────────────────────
// Request interceptor — inject bearer token
// ─────────────────────────────────────────────────────────────────────────────

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─────────────────────────────────────────────────────────────────────────────
// Response interceptor — automatic token refresh on 401
// ─────────────────────────────────────────────────────────────────────────────

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // Auth endpoints must not trigger refresh loops
      if (
        originalRequest.url.includes("/auth/refresh") ||
        originalRequest.url.includes("/auth/login")
      ) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await apiClient.post("/api/v1/auth/refresh");
        const newAccessToken = response.data.data.access_token;
        localStorage.setItem("access_token", newAccessToken);
        apiClient.defaults.headers.common["Authorization"] = `Bearer ${newAccessToken}`;
        originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        isRefreshing = false;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        if (window.onAuthExpired) {
          window.onAuthExpired();
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// Typed service namespaces — one per resource
// ─────────────────────────────────────────────────────────────────────────────

/** Disaster records and inference */
export const disastersApi = {
  list: (params = {}) => apiClient.get("/api/v1/disasters", { params }),
  create: (payload) => apiClient.post("/api/v1/predict/disaster", payload),
  delete: (id) => apiClient.delete(`/api/v1/disasters/${id}`),
};

/** Alerts (linked to disasters) */
export const alertsApi = {
  list: (params = {}) => apiClient.get("/api/v1/alerts", { params }),
  acknowledge: (id) => apiClient.patch(`/api/v1/alerts/${id}/acknowledge`),
};

/** Incident reports */
export const reportsApi = {
  list: (params = {}) => apiClient.get("/api/v1/reports", { params }),
  create: (payload) => apiClient.post("/api/v1/reports", payload),
  delete: (id) => apiClient.delete(`/api/v1/reports/${id}`),
};

/** Authenticated user profile */
export const meApi = {
  get: () => apiClient.get("/api/v1/auth/me"),
  update: (payload) => apiClient.put("/api/v1/auth/me", payload),
};

/** Backend health check */
export const healthApi = {
  readiness: () => apiClient.get("/readiness"),
};

export default apiClient;
