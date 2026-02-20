import { useState, useEffect } from "react";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("access_token");
    if (token) {
      setIsAuthenticated(true);
      // TODO: Fetch user info on Fase 2 with Keycloak
    }
    setLoading(false);
  }, []);

  const login = (username, password) => {
    // TODO: Implement Keycloak login on Fase 2
    console.log("Mock login:", username);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setIsAuthenticated(false);
  };

  return { user, loading, isAuthenticated, login, logout };
}
