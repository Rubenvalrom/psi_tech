import axios from "axios";
import { User } from "oidc-client-ts";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

function getAccessToken() {
  const oidcStorage = sessionStorage.getItem(
    "oidc.user:http://localhost:8080/realms/olympus:olympus-frontend"
  );
  if (!oidcStorage) {
    return null;
  }
  return User.fromStorageString(oidcStorage)?.access_token;
}

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      sessionStorage.removeItem("oidc.user:http://localhost:8080/realms/olympus:olympus-frontend");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
