import { useAuth as useOidcAuth } from "react-oidc-context";
import { useEffect } from "react";

export function useAuth() {
  const auth = useOidcAuth();

  useEffect(() => {
    console.log("🔍 useAuth hook state:", {
      isLoading: auth.isLoading,
      isAuthenticated: auth.isAuthenticated,
      hasUser: !!auth.user,
      userName: auth.user?.profile?.preferred_username,
      hasToken: !!auth.user?.access_token,
      error: auth.error?.message,
    });
  }, [auth.isLoading, auth.isAuthenticated, auth.user, auth.error]);

  return {
    user: auth.user?.profile,
    loading: auth.isLoading,
    isAuthenticated: auth.isAuthenticated,
    login: () => auth.signinRedirect(),
    logout: () => auth.signoutRedirect(),
    token: auth.user?.access_token,
    error: auth.error,
  };
}
