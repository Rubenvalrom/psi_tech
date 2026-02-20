import { useState } from "react";
import { Layout } from "../components/Layout";
import api from "../services/api";

export function AsistenteIA() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setLoading(true);
    setAnswer("");
    setSources([]);
    
    try {
      const response = await api.post(`/ai/ask?question=${encodeURIComponent(question)}`);
      setAnswer(response.data.answer);
      setSources(response.data.sources);
    } catch (err) {
      alert("Error consultando al asistente: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSemanticSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setSearchLoading(true);
    try {
      const response = await api.post(`/ai/search/semantic?query=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
    } catch (err) {
      alert("Error en búsqueda semántica: " + err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Asistente IA ✨</h1>
        <p className="text-gray-600 mt-2">Búsqueda semántica y respuestas inteligentes con RAG</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Assistant RAG */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-blue-100 h-fit">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            💬 Pregunta al Asistente
          </h2>
          <form onSubmit={handleAsk} className="space-y-4">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ej: ¿Qué facturas tenemos pendientes del proveedor Olympus Tech?"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 h-24"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 disabled:bg-blue-300 transition"
            >
              {loading ? "Pensando..." : "Consultar IA"}
            </button>
          </form>

          {answer && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-bold text-blue-800 mb-2">Respuesta:</h3>
              <p className="text-blue-900 text-sm leading-relaxed">{answer}</p>
              
              {sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <h4 className="text-xs font-bold text-blue-700 uppercase mb-2">Fuentes utilizadas:</h4>
                  <ul className="space-y-1">
                    {sources.map(s => (
                      <li key={s.id} className="text-xs text-blue-600">• {s.nombre} (Expediente {s.expediente_id})</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Semantic Search */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-purple-100">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            🔍 Búsqueda Semántica
          </h2>
          <form onSubmit={handleSemanticSearch} className="flex gap-2 mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Busca por significado..."
              className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="submit"
              disabled={searchLoading}
              className="bg-purple-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-purple-700 transition"
            >
              {searchLoading ? "..." : "Buscar"}
            </button>
          </form>

          <div className="space-y-4">
            {searchResults.length === 0 && !searchLoading && (
              <p className="text-center text-gray-400 py-8 italic">No hay resultados semánticos.</p>
            )}
            
            {searchResults.map((res) => (
              <div key={res.id} className="p-4 border rounded-lg hover:border-purple-300 transition group cursor-pointer">
                <div className="flex justify-between items-start mb-1">
                  <h3 className="font-bold text-gray-900 group-hover:text-purple-600">{res.nombre}</h3>
                  <span className="text-xs font-mono text-gray-400">Exp: {res.expediente_id}</span>
                </div>
                <p className="text-xs text-gray-500 uppercase tracking-wider">{res.tipo}</p>
                {res.metadatos?.resumen && (
                  <p className="text-sm text-gray-600 mt-2 italic">"{res.metadatos.resumen}"</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
