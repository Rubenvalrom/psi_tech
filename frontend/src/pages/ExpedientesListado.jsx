import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Layout } from "../components/Layout";
import { ToastContainer } from "../components/Toast";
import useToast from "../hooks/useToast";
import api from "../services/api";

const ITEMS_PER_PAGE = 10;

export function ExpedientesListado() {
  const { toasts, addToast, removeToast } = useToast();
  const [expedientes, setExpedientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  useEffect(() => {
    fetchExpedientes(currentPage);
  }, [currentPage]);

  const fetchExpedientes = async (page) => {
    setLoading(true);
    setError(null);
    try {
      const skip = (page - 1) * ITEMS_PER_PAGE;
      const response = await api.get(`/expedientes?skip=${skip}&limit=${ITEMS_PER_PAGE}`);
      setExpedientes(response.data.items || []);
      setTotalItems(response.data.total || 0);
    } catch (err) {
      const errorMsg = err.message || "Error cargando expedientes";
      setError(errorMsg);
      addToast(errorMsg, "error");
      console.error("Error fetching expedientes:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePageClick = (page) => {
    setCurrentPage(page);
  };

  if (loading) return <Layout><div className="p-4">Cargando...</div></Layout>;

  return (
    <Layout>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Expedientes</h1>
          <p className="text-gray-600 mt-2">Gestión de expedientes administrativos</p>
          <p className="text-sm text-gray-500 mt-1">Mostrando {expedientes.length} de {totalItems} expedientes</p>
        </div>
        <Link
          to="/expedientes/nuevo"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          Nuevo Expediente
        </Link>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          Error: {error}
        </div>
      )}

      {expedientes.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow text-center">
          <p className="text-gray-600">No hay expedientes disponibles</p>
        </div>
      ) : (
        <div className="space-y-6">
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
                  <tr key={exp.id} className="border-t hover:bg-gray-50 transition">
                    <td className="px-6 py-3 text-sm text-gray-900 font-medium">{exp.numero}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{exp.asunto}</td>
                    <td className="px-6 py-3 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        exp.estado === 'ABIERTO' ? 'bg-green-100 text-green-800' :
                        exp.estado === 'EN_PROCESO' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {exp.estado}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <Link
                        to={`/expedientes/${exp.id}`}
                        className="text-blue-600 hover:text-blue-900 font-medium transition"
                      >
                        Ver detalles
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Página {currentPage} de {totalPages}
            </div>

            <div className="flex gap-2">
              <button
                onClick={handlePreviousPage}
                disabled={currentPage === 1}
                className={`px-4 py-2 rounded border transition ${
                  currentPage === 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                ← Anterior
              </button>

              <div className="flex gap-1">
                {Array.from({ length: Math.min(5, totalPages) }).map((_, idx) => {
                  let page;
                  if (totalPages <= 5) {
                    page = idx + 1;
                  } else if (currentPage <= 3) {
                    page = idx + 1;
                  } else if (currentPage >= totalPages - 2) {
                    page = totalPages - 4 + idx;
                  } else {
                    page = currentPage - 2 + idx;
                  }

                  return (
                    <button
                      key={page}
                      onClick={() => handlePageClick(page)}
                      className={`px-3 py-2 rounded transition ${
                        currentPage === page
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}
              </div>

              <button
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
                className={`px-4 py-2 rounded border transition ${
                  currentPage === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                Siguiente →
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
