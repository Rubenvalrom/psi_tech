import { useEffect } from "react";
import { useAuth } from "../hooks/useAuth";

export function Login() {
  const { login } = useAuth();

  useEffect(() => {
    login();
  }, [login]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-blue-50">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Olympus Smart Gov
        </h1>
        <p className="text-center text-gray-600 mb-6">
          Redirigiendo a Keycloak...
        </p>
      </div>
    </div>
  );
}
