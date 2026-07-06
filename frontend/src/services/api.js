import axios from "axios";

// Resolves backend API URL dynamically based on client location
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
  withCredentials: true,  // Required to transmit secure HTTP-only cookies
});

// Interceptor injecting bearer token into headers
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

// Interceptor managing automatic token refresh retry queues
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

    // Trigger refresh flow on 401 Unauthorized errors
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
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
        
        // Notify application components of session expiry
        if (window.onAuthExpired) {
          window.onAuthExpired();
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
