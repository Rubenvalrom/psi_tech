import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Layout } from "../components/Layout";
import api from "../services/api";

export function ExpedientesListado() {
  const [expedientes, setExpedientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchExpedientes();
  }, []);

  const fetchExpedientes = async () => {
    try {
      const response = await api.get("/expedientes?skip=0&limit=10");
      setExpedientes(response.data.items);
    } catch (err) {
      setError(err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><div className="p-4">Cargando...</div></Layout>;
  if (error) return <Layout><div className="p-4 text-red-600">Error: {error}</div></Layout>;

  return (
    <Layout>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Expedientes</h1>
          <p className="text-gray-600 mt-2">Case files management</p>
        </div>
        <Link
          to="/expedientes/nuevo"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Nuevo Expediente
        </Link>
      </div>

      {expedientes.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow text-center">
          <p className="text-gray-600">No expedientes available</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Número
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Asunto
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Acción
                </th>
              </tr>
            </thead>
            <tbody>
              {expedientes.map((exp) => (
                <tr key={exp.id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm text-gray-900">{exp.numero}</td>
                  <td className="px-6 py-3 text-sm text-gray-900">{exp.asunto}</td>
                  <td className="px-6 py-3 text-sm">
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                      {exp.estado}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-sm">
                    <Link
                      to={`/expedientes/${exp.id}`}
                      className="text-blue-600 hover:text-blue-900 font-medium"
                    >
                      Ver
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  );
}
