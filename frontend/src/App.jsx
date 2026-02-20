import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ExpedientesListado } from "./pages/ExpedientesListado";
import { ExpedienteDetalle } from "./pages/ExpedienteDetalle";
import { AsistenteIA } from "./pages/AsistenteIA";
import { PresupuestosPage } from "./pages/PresupuestosPage";
import { useAuth } from "./hooks/useAuth";

// Pantalla de carga inicial (mientras carga el AuthProvider)
function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      {/* Fondo con gradiente animado */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"></div>
      
      {/* Contenido centrado */}
      <div className="relative z-10 text-center">
        {/* Spinner elegante */}
        <div className="mb-8 flex justify-center">
          <div className="relative w-20 h-20">
            {/* Círculo exterior rotante */}
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-600 border-r-indigo-600 animate-spin"></div>
            {/* Círculo interior animado */}
            <div className="absolute inset-2 rounded-full border-2 border-transparent border-b-purple-600 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
            {/* Icono central */}
            <div className="absolute inset-0 flex items-center justify-center text-blue-600">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>
        
        {/* Texto */}
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Iniciando Olympus</h2>
        <p className="text-sm text-gray-500">Preparando tu sesión...</p>
        
        {/* Barra de progreso animada */}
        <div className="mt-8 w-48 h-1 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full animate-pulse" 
            style={{ animation: 'shimmer 1.5s infinite' }}></div>
        </div>
      </div>
    </div>
  );
}

// Pantalla de redirección a Keycloak (verificando credenciales)
function VerifyingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      {/* Fondo con gradiente animado - más enfocado en verde/blue */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-blue-500 to-indigo-600"></div>
      
      {/* Luces de fondo decorativas */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
      </div>
      
      {/* Contenido centrado */}
      <div className="relative z-10 text-center px-6">
        {/* Contenedor de la tarjeta */}
        <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-12 max-w-md">
          {/* Icono con animación */}
          <div className="mb-8 flex justify-center">
            <div className="relative w-24 h-24">
              {/* Círculo de fondo pulsante */}
              <div className="absolute inset-0 rounded-full bg-blue-100 animate-pulse"></div>
              
              {/* Icono principal con animación de "paso" */}
              <div className="absolute inset-0 flex items-center justify-center text-blue-600">
                <svg className="w-12 h-12 animate-bounce" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
              </div>
              
              {/* Anillo rotante */}
              <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-blue-500 border-r-indigo-500 animate-spin"></div>
            </div>
          </div>
          
          {/* Textos */}
          <h2 className="text-2xl font-bold text-gray-800 mb-3">Verificando</h2>
          <p className="text-gray-600 text-sm mb-8">Autenticando tu sesión con Keycloak...</p>
          
          {/* Indicador de progreso con puntos */}
          <div className="flex justify-center gap-2 mb-6">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
          </div>
          
          {/* Mensaje adicional */}
          <p className="text-xs text-gray-400">No cierres esta ventana...</p>
        </div>
        
        {/* Elemento flotante decorativo abajo */}
        <div className="mt-12 text-white/50 text-sm">
          <p>Proceso de seguridad en progreso</p>
        </div>
      </div>
    </div>
  );
}

function AppRouter() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Ruta raíz: redirige según estado de autenticación */}
      <Route
        path="/"
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (window.location.search.includes("code=") ? (
            <VerifyingScreen />
          ) : (
            <Navigate to="/login" replace />
          ))
        }
      />

      <Route
        path="/dashboard"
        element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
      />
      <Route
        path="/expedientes"
        element={<ProtectedRoute><ExpedientesListado /></ProtectedRoute>}
      />
      <Route
        path="/expedientes/:id"
        element={<ProtectedRoute><ExpedienteDetalle /></ProtectedRoute>}
      />
      <Route
        path="/presupuestos"
        element={<ProtectedRoute><PresupuestosPage /></ProtectedRoute>}
      />
      <Route
        path="/asistente-ia"
        element={<ProtectedRoute><AsistenteIA /></ProtectedRoute>}
      />

      {/* Catch-all: redirige a dashboard o login */}
      <Route 
        path="*" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} 
      />
    </Routes>
  );
}

function App() {
  const { loading, isAuthenticated, error } = useAuth();

  // 1. Si hay un error crítico de autenticación, mostramos el error para diagnosticar
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50 p-4">
        <div className="bg-white p-8 rounded-lg shadow-xl border-t-4 border-red-500 max-w-md w-full">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Error de Conexión</h2>
          <p className="text-gray-700 mb-4 font-medium">No pudimos validar tu sesión con Keycloak.</p>
          <div className="bg-gray-100 p-3 rounded text-xs font-mono text-gray-600 mb-6 break-all">
            {error.message}
          </div>
          <button 
            onClick={() => window.location.href = "/"}
            className="w-full bg-red-600 text-white py-2 rounded font-bold hover:bg-red-700 transition"
          >
            Intentar de nuevo
          </button>
        </div>
      </div>
    );
  }

  // 2. Mientras el sistema inicia, mostramos pantalla de carga
  if (loading) {
    return <LoadingScreen />;
  }

  // 3. Si hay un código en la URL Y estamos cargando, mostramos "Verificando..."
  //    (react-oidc-context está procesando el código en el background)
  const hasParams = window.location.search.includes("code=") || window.location.search.includes("state=");
  if (hasParams && loading) {
    return <VerifyingScreen />;
  }

  // 4. Renderiza el router con todas las rutas
  return <AppRouter />;
}

export default App;