import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "react-oidc-context";
import App from "./App.jsx";
import "./index.css";

const oidcConfig = {
  authority: "http://localhost:8080/realms/olympus",
  client_id: "olympus-frontend",
  redirect_uri: window.location.origin,
  onSigninCallback: () => {
    // Remove query string after successful login
    window.history.replaceState({}, document.title, window.location.pathname);
  },
  post_logout_redirect_uri: window.location.origin
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
