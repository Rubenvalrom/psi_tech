import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "react-oidc-context";
import App from "./App.jsx";
import "./index.css";

const authority = import.meta.env.VITE_AUTH_AUTHORITY || "http://localhost:8080/realms/olympus";
const redirect_uri = window.location.origin; // Usar origen dinámico para evitar discrepancias

const oidcConfig = {
  authority,
  client_id: "olympus-frontend",
  redirect_uri,
  response_type: "code",
  scope: "openid profile email",
  
  // Configuración de usuario y token
  loadUserInfo: true,
  automaticSilentRenew: true,
  monitorSession: false, // Desactivar en desarrollo/incógnito para evitar bloqueos de iframe
  
  // Callbacks
  onSigninCallback: (_user) => {
    console.log("✅ OIDC Signin Callback successful. User authenticated.");
    // Limpia los parámetros de la URL (?code=...&state=...) tras el login exitoso
    window.history.replaceState({}, document.title, window.location.pathname);
  },
  onSigninError: (error) => {
    console.error("❌ OIDC Signin Error:", error);
  }
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
