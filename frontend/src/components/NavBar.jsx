import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function NavBar() {
  const { logout } = useAuth();

  return (
    <nav className="bg-blue-600 text-white p-4 shadow">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/dashboard" className="text-2xl font-bold">
          Olympus Smart Gov
        </Link>
        <div className="flex gap-6">
          <Link to="/dashboard" className="hover:text-blue-200">
            Dashboard
          </Link>
          <Link to="/expedientes" className="hover:text-blue-200">
            Expedientes
          </Link>
          <Link to="/presupuestos" className="hover:text-blue-200">
            Presupuestos
          </Link>
          <button
            onClick={logout}
            className="bg-red-500 px-4 py-2 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
