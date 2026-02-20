import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  // Mientras se verifica la sesión con Keycloak, mostramos un spinner para evitar redirecciones prematuras
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="ml-4 text-gray-600 font-medium">Verificando sesión...</p>
      </div>
    );
  }

  // Solo si la carga ha terminado y NO está autenticado, mandamos al login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
