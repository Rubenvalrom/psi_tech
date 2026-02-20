import axios from "axios";
import { User } from "oidc-client-ts";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

function getAccessToken() {
  // Try to find any OIDC user key in sessionStorage
  // oidc-client-ts keys follow the pattern: oidc.user:<authority>:<client_id>
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    if (key && key.startsWith("oidc.user:")) {
      const oidcStorage = sessionStorage.getItem(key);
      if (oidcStorage) {
        try {
          const user = User.fromStorageString(oidcStorage);
          if (user && user.access_token && !user.expired) {
            return user.access_token;
          }
        } catch (e) {
          console.error(`Error parsing token from key "${key}":`, e);
        }
      }
    }
  }
  return null;
}

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn("🚫 401 Unauthorized detected at:", error.config.url);
      
      // Limpiar rastro de sesión de forma segura
      const keysToRemove = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.startsWith("oidc.user:") || key.startsWith("oidc.state:"))) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => sessionStorage.removeItem(key));

      // Solo redirigir si no estamos ya en la página de login
      if (!window.location.pathname.includes("/login")) {
        window.location.href = "/login?reason=session_expired";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
