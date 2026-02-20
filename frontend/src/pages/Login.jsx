import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function Login() {
  const { login, isAuthenticated, loading, error } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated, navigate]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50 p-4">
        <div className="bg-white p-8 rounded-lg shadow-xl border-t-4 border-red-500 max-w-md w-full">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Error de Identidad</h2>
          <p className="text-gray-600 mb-6 font-mono text-xs bg-gray-100 p-2 rounded break-all">{error.message}</p>
          <button onClick={() => window.location.href = "/"} className="w-full bg-red-600 text-white py-2 rounded font-bold">
            Reiniciar Aplicación
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-blue-50">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md text-center">
        <h1 className="text-3xl font-bold mb-6 text-blue-600">Olympus Smart Gov</h1>
        {loading ? (
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        ) : (
          <>
            <p className="text-gray-600 mb-6">Inicie sesión para acceder a la plataforma pública.</p>
            <button 
              onClick={() => login()}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition"
            >
              Entrar con Keycloak
            </button>
          </>
        )}
      </div>
    </div>
  );
}
