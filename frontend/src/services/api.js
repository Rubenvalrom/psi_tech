import axios from "axios";
import { User } from "oidc-client-ts";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

function getAccessToken() {
  const authority = import.meta.env.VITE_AUTH_AUTHORITY || "http://localhost:8080/realms/olympus";
  const clientId = "olympus-frontend";
  
  // Construct the expected OIDC storage key
  const oidcKey = `oidc.user:${authority}:${clientId}`;
  const oidcStorage = sessionStorage.getItem(oidcKey);
  
  if (oidcStorage) {
    try {
      return User.fromStorageString(oidcStorage)?.access_token;
    } catch (e) {
      console.error(`Error parsing token from key "${oidcKey}":`, e);
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
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
