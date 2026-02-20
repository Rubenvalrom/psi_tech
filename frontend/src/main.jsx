import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "react-oidc-context";
import App from "./App.jsx";
import "./index.css";

const authority = import.meta.env.VITE_AUTH_AUTHORITY || "http://localhost:8080/realms/olympus";
const redirect_uri = import.meta.env.VITE_AUTH_REDIRECT_URI || "http://localhost:3000";

const oidcConfig = {
  authority,
  client_id: "olympus-frontend",
  redirect_uri,
  response_type: "code",
  scope: "openid profile email",
  
  // Configuración de usuario y token
  loadUserInfo: true,
  automaticSilentRenew: true,
  
  // Callbacks
  onSigninCallback: (user) => {
    console.log("✅ [OIDC] Login exitoso. Usuario:", user?.profile?.preferred_username);
    console.log("✅ [OIDC] Token guard:", !!user?.access_token);
  },
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
