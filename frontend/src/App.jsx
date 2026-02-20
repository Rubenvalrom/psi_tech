import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ExpedientesListado } from "./pages/ExpedientesListado";
import { ExpedienteDetalle } from "./pages/ExpedienteDetalle";
import { AsistenteIA } from "./pages/AsistenteIA";
import { PresupuestosPage } from "./pages/PresupuestosPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/expedientes"
          element={
            <ProtectedRoute>
              <ExpedientesListado />
            </ProtectedRoute>
          }
        />
        <Route
          path="/expedientes/:id"
          element={
            <ProtectedRoute>
              <ExpedienteDetalle />
            </ProtectedRoute>
          }
        />
        <Route
          path="/presupuestos"
          element={
            <ProtectedRoute>
              <PresupuestosPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/asistente-ia"
          element={
            <ProtectedRoute>
              <AsistenteIA />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
