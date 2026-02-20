import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Layout } from "../components/Layout";
import Modal from "../components/Modal";
import { ToastContainer } from "../components/Toast";
import useToast from "../hooks/useToast";
import api from "../services/api";

export function ExpedienteDetalle() {
  const { id } = useParams();
  const { toasts, addToast, removeToast } = useToast();
  const [expediente, setExpediente] = useState(null);
  const [pasos, setPasos] = useState([]);
  const [trazabilidad, setTrazabilidad] = useState([]);
  const [facturas, setFacturas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("pasos");
  const [modal, setModal] = useState({ isOpen: false, type: "info", title: "", message: "" });

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const results = await Promise.allSettled([
        api.get(`/expedientes/${id}`),
        api.get(`/expedientes/${id}/pasos`),
        api.get(`/expedientes/${id}/trazabilidad`),
        api.get(`/finanzas/facturas?expediente_id=${id}`)
      ]);

      // Check each result individually
      if (results[0].status === "fulfilled") {
        setExpediente(results[0].value.data);
      } else {
        setError("Error cargando expediente");
        addToast("Error cargando expediente", "error");
      }

      if (results[1].status === "fulfilled") {
        setPasos(results[1].value.data || []);
      }

      if (results[2].status === "fulfilled") {
        setTrazabilidad(results[2].value.data || []);
      }

      if (results[3].status === "fulfilled") {
        setFacturas(results[3].value.data || []);
      }
    } catch (err) {
      const errorMsg = err.message || "Error inesperado cargando datos";
      setError(errorMsg);
      addToast(errorMsg, "error");
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteStep = async (pasoId) => {
    try {
      await api.post(`/expedientes/${id}/pasos/${pasoId}/complete`, null, {
        params: { comentarios: "Completado desde la UI" }
      });
      addToast("Paso completado correctamente", "success");
      fetchData();
    } catch (err) {
      addToast(`Error completando paso: ${err.message}`, "error");
      console.error("Error completing step:", err);
    }
  };

  const handleSignDocument = async (docId) => {
    setModal({
      isOpen: true,
      type: "info",
      title: "Firmar Documento",
      message: "Esto debería abrir un diálogo para tu nombre/cargo",
      onConfirm: async () => {
        const firmado_por = prompt("Introduce tu nombre/cargo para firmar:");
        if (!firmado_por) return;
        
        try {
          await api.post(`/expedientes/documentos/${docId}/sign`, { firmado_por });
          addToast("Documento firmado correctamente", "success");
          fetchData();
        } catch (err) {
          addToast(`Error firmando documento: ${err.message}`, "error");
          console.error("Error signing document:", err);
        }
      }
    });
  };

  const handleStartExpediente = async () => {
    try {
      await api.post(`/expedientes/${id}/start`);
      addToast("Tramitación iniciada correctamente", "success");
      fetchData();
    } catch (err) {
      addToast(`Error iniciando tramitación: ${err.message}`, "error");
      console.error("Error starting expediente:", err);
    }
  };

  const handleUploadDocument = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size and type
    const MAX_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/png", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
    
    if (!ALLOWED_TYPES.includes(file.type)) {
      addToast("Tipo de archivo no permitido. Usa PDF, JPG, PNG o Word.", "warning");
      return;
    }

    if (file.size > MAX_SIZE) {
      addToast("El archivo excede 10MB. Por favor, elige uno más pequeño.", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    
    try {
      await api.post(`/expedientes/${id}/documentos`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      addToast("Documento subido. Análisis IA en segundo plano.", "success");
      fetchData();
    } catch (err) {
      addToast(`Error subiendo documento: ${err.message}`, "error");
      console.error("Error uploading document:", err);
    }
  };

  const handleAddFactura = async () => {
    const numero = prompt("Número de factura:");
    if (!numero) return;

    const monto = prompt("Monto:");
    if (!monto || isNaN(parseFloat(monto))) {
      addToast("Monto inválido", "warning");
      return;
    }

    const proveedor = prompt("Proveedor:");
    if (!proveedor) return;

    try {
      await api.post('/finanzas/facturas', {
        numero,
        monto: parseFloat(monto),
        proveedor,
        fecha_emision: new Date().toISOString(),
        expediente_id: parseInt(id)
      });
      addToast("Factura registrada correctamente", "success");
      fetchData();
    } catch (err) {
      addToast(`Error registrando factura: ${err.message}`, "error");
      console.error("Error adding invoice:", err);
    }
  };

  if (loading) return <Layout><div className="p-4">Cargando...</div></Layout>;
  if (error && !expediente) return <Layout><div className="p-4 text-red-600">Error: {error}</div></Layout>;
  if (!expediente) return <Layout><div className="p-4">Expediente no encontrado</div></Layout>;

  return (
    <Layout>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <Modal {...modal} />

      <div className="mb-6 flex justify-between items-start">
        <div>
          <div className="flex items-center gap-3">
            <Link to="/expedientes" className="text-blue-600 hover:underline">← Volver</Link>
            <h1 className="text-3xl font-bold text-gray-900">{expediente?.numero}</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              expediente?.estado === 'ABIERTO' ? 'bg-green-100 text-green-800' :
              expediente?.estado === 'EN_PROCESO' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {expediente?.estado}
            </span>
          </div>
          <p className="text-gray-600 mt-2 font-medium">{expediente?.asunto}</p>
        </div>
        
        {expediente?.estado === 'ABIERTO' && (
          <button 
            onClick={handleStartExpediente}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Iniciar Tramitación
          </button>
        )}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {['pasos', 'documentos', 'trazabilidad', 'finanzas'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                    activeTab === tab 
                      ? 'border-blue-500 text-blue-600' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            {activeTab === 'pasos' && (
              <div className="space-y-8">
                {(pasos?.length ?? 0) === 0 ? <p className="text-gray-500 italic">No hay pasos definidos.</p> : (
                  <div className="relative">
                    {pasos.map((paso, idx) => (
                      <div key={paso.id} className="mb-10 flex items-start last:mb-0">
                        <div className="flex flex-col items-center mr-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold border-2 ${
                            paso.estado === 'COMPLETADO' ? 'bg-green-500 border-green-500 text-white' :
                            paso.estado === 'EN_PROGRESO' ? 'bg-blue-500 border-blue-500 text-white' :
                            'bg-white border-gray-300 text-gray-400'
                          }`}>
                            {paso.estado === 'COMPLETADO' ? '✓' : paso.numero_paso}
                          </div>
                          {idx !== (pasos?.length ?? 0) - 1 && <div className="w-0.5 h-full bg-gray-200 my-2"></div>}
                        </div>
                        <div className="flex-1 pt-1">
                          <h3 className="text-lg font-bold text-gray-900">{paso.titulo}</h3>
                          <p className="text-gray-600 text-sm mt-1">{paso.descripcion}</p>
                          {paso.estado !== 'COMPLETADO' && (
                            <button 
                              onClick={() => handleCompleteStep(paso.id)}
                              className="mt-3 text-sm bg-gray-50 text-blue-600 border border-blue-200 px-3 py-1 rounded hover:bg-blue-50 transition"
                            >
                              Marcar como completado
                            </button>
                          )}
                          {paso.datetime_fin && (
                            <p className="text-xs text-gray-400 mt-2 italic">Finalizado el: {new Date(paso.datetime_fin).toLocaleString()}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'documentos' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Documentos Adjuntos</h3>
                  <label htmlFor="document-upload" className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold hover:bg-blue-700 shadow-sm transition">
                    Subir Documento
                  </label>
                  <input
                    id="document-upload"
                    type="file"
                    className="hidden"
                    onChange={handleUploadDocument}
                  />
                </div>
                {(expediente?.documentos?.length ?? 0) === 0 ? <p className="text-gray-500 italic">No hay documentos adjuntos.</p> : (
                  (expediente?.documentos ?? []).map(doc => (
                    <div key={doc.id} className="flex justify-between items-center p-4 border rounded-lg hover:bg-gray-50 transition">
                      <div className="flex-1">
                        <p className="font-bold text-gray-900">{doc.nombre}</p>
                        <p className="text-xs text-gray-500 uppercase tracking-wider">{doc.tipo}</p>
                        {doc.hash_firma ? (
                          <div className="mt-2 bg-green-50 p-2 rounded border border-green-100">
                            <p className="text-xs text-green-700 font-mono break-all">
                              <span className="font-bold">Firma SHA-256:</span> {doc.hash_firma}
                            </p>
                            <p className="text-xs text-green-700 mt-1">Firmado por: {doc.firmado_por}</p>
                          </div>
                        ) : (
                          <p className="text-xs text-orange-600 mt-2 flex items-center gap-1 italic">
                            ⚠️ Pendiente de firma
                          </p>
                        )}
                        {doc.metadatos_extraidos && (
                          <div className="mt-2 bg-blue-50 p-2 rounded border border-blue-100">
                            <p className="text-xs text-blue-700 font-bold">Metadatos Extraídos (IA):</p>
                            <pre className="text-xs text-blue-700 font-mono whitespace-pre-wrap">
                              {(() => {
                                try {
                                  return JSON.stringify(JSON.parse(doc.metadatos_extraidos), null, 2);
                                } catch (e) {
                                  return "[Error: Invalid JSON format]";
                                }
                              })()}
                            </pre>
                          </div>
                        )}
                      </div>
                      {!doc.hash_firma && (
                        <button 
                          onClick={() => handleSignDocument(doc.id)}
                          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold hover:bg-blue-700 shadow-sm transition whitespace-nowrap ml-4"
                        >
                          Firmar Digitalmente
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'trazabilidad' && (
              <div className="space-y-4">
                {(trazabilidad?.length ?? 0) === 0 ? (
                  <p className="text-gray-500 italic">No hay registros de trazabilidad.</p>
                ) : (
                  trazabilidad.map(log => (
                    <div key={log.id} className="flex gap-4 p-3 border-l-4 border-blue-500 bg-gray-50 rounded-r-lg">
                      <div className="text-xs font-mono text-gray-400 whitespace-nowrap pt-1">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-gray-900">{log.accion}</p>
                        <p className="text-sm text-gray-600">{log.descripcion}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'finanzas' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Facturas Asociadas</h3>
                  <button 
                    onClick={handleAddFactura}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm"
                  >
                    + Registrar Factura
                  </button>
                </div>
                
                {(facturas?.length ?? 0) === 0 ? <p className="text-gray-500 italic">No hay facturas registradas.</p> : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-500">
                      <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                          <th className="px-6 py-3">Número</th>
                          <th className="px-6 py-3">Proveedor</th>
                          <th className="px-6 py-3">Fecha</th>
                          <th className="px-6 py-3">Monto</th>
                          <th className="px-6 py-3">Estado</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(facturas ?? []).map((fac) => (
                          <tr key={fac.id} className="bg-white border-b hover:bg-gray-50">
                            <td className="px-6 py-4 font-medium text-gray-900">{fac.numero}</td>
                            <td className="px-6 py-4">{fac.proveedor}</td>
                            <td className="px-6 py-4">{new Date(fac.fecha_emision).toLocaleDateString()}</td>
                            <td className="px-6 py-4 font-bold text-gray-900">{fac.monto} €</td>
                            <td className="px-6 py-4">
                              <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                                fac.estado === 'PAGADA' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {fac.estado}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Detalles</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-500 block">Responsable</label>
                <p className="text-sm font-medium text-gray-900">ID Usuario: {expediente?.responsable_id || 'Sin asignar'}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500 block">Fecha Creación</label>
                <p className="text-sm font-medium text-gray-900">{expediente?.fecha_creacion ? new Date(expediente.fecha_creacion).toLocaleDateString() : 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500 block">Última Actualización</label>
                <p className="text-sm font-medium text-gray-900">{expediente?.fecha_actualizacion ? new Date(expediente.fecha_actualizacion).toLocaleString() : 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

  return (
    <Layout>
      <div className="mb-6 flex justify-between items-start">
        <div>
          <div className="flex items-center gap-3">
            <Link to="/expedientes" className="text-blue-600 hover:underline">← Volver</Link>
            <h1 className="text-3xl font-bold text-gray-900">{expediente.numero}</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              expediente.estado === 'ABIERTO' ? 'bg-green-100 text-green-800' :
              expediente.estado === 'EN_PROCESO' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {expediente.estado}
            </span>
          </div>
          <p className="text-gray-600 mt-2 font-medium">{expediente.asunto}</p>
        </div>
        
        {expediente.estado === 'ABIERTO' && (
          <button 
            onClick={async () => { await api.post(`/expedientes/${id}/start`); fetchData(); }}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Iniciar Tramitación
          </button>
        )}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {['pasos', 'documentos', 'trazabilidad', 'finanzas'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                    activeTab === tab 
                      ? 'border-blue-500 text-blue-600' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            {activeTab === 'pasos' && (
              <div className="space-y-8">
                {pasos.length === 0 ? <p className="text-gray-500 italic">No hay pasos definidos.</p> : (
                  <div className="relative">
                    {pasos.map((paso, idx) => (
                      <div key={paso.id} className="mb-10 flex items-start last:mb-0">
                        <div className="flex flex-col items-center mr-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold border-2 ${
                            paso.estado === 'COMPLETADO' ? 'bg-green-500 border-green-500 text-white' :
                            paso.estado === 'EN_PROGRESO' ? 'bg-blue-500 border-blue-500 text-white' :
                            'bg-white border-gray-300 text-gray-400'
                          }`}>
                            {paso.estado === 'COMPLETADO' ? '✓' : paso.numero_paso}
                          </div>
                          {idx !== pasos.length - 1 && <div className="w-0.5 h-full bg-gray-200 my-2"></div>}
                        </div>
                        <div className="flex-1 pt-1">
                          <h3 className="text-lg font-bold text-gray-900">{paso.titulo}</h3>
                          <p className="text-gray-600 text-sm mt-1">{paso.descripcion}</p>
                          {paso.estado !== 'COMPLETADO' && (
                            <button 
                              onClick={() => handleCompleteStep(paso.id)}
                              className="mt-3 text-sm bg-gray-50 text-blue-600 border border-blue-200 px-3 py-1 rounded hover:bg-blue-50 transition"
                            >
                              Marcar como completado
                            </button>
                          )}
                          {paso.datetime_fin && (
                            <p className="text-xs text-gray-400 mt-2 italic">Finalizado el: {new Date(paso.datetime_fin).toLocaleString()}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'documentos' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Documentos Adjuntos</h3>
                  <label htmlFor="document-upload" className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold hover:bg-blue-700 shadow-sm transition">
                    Subir Documento
                  </label>
                  <input
                    id="document-upload"
                    type="file"
                    className="hidden"
                    onChange={async (e) => {
                      const file = e.target.files[0];
                      if (!file) return;
                      const formData = new FormData();
                      formData.append("file", file);
                      try {
                        await api.post(`/expedientes/${id}/documentos`, formData, {
                          headers: { "Content-Type": "multipart/form-data" },
                        });
                        fetchData();
                        alert("Documento subido y análisis IA en segundo plano.");
                      } catch (err) {
                        alert("Error subiendo documento: " + err.message);
                      }
                    }}
                  />
                </div>
                {expediente.documentos.length === 0 ? <p className="text-gray-500 italic">No hay documentos adjuntos.</p> : (
                  expediente.documentos.map(doc => (
                    <div key={doc.id} className="flex justify-between items-center p-4 border rounded-lg hover:bg-gray-50 transition">
                      <div>
                        <p className="font-bold text-gray-900">{doc.nombre}</p>
                        <p className="text-xs text-gray-500 uppercase tracking-wider">{doc.tipo}</p>
                        {doc.hash_firma ? (
                          <div className="mt-2 bg-green-50 p-2 rounded border border-green-100">
                            <p className="text-xs text-green-700 font-mono break-all">
                              <span className="font-bold">Firma SHA-256:</span> {doc.hash_firma}
                            </p>
                            <p className="text-xs text-green-700 mt-1">Firmado por: {doc.firmado_por}</p>
                          </div>
                        ) : (
                          <p className="text-xs text-orange-600 mt-2 flex items-center gap-1 italic">
                            ⚠️ Pendiente de firma
                          </p>
                        )}
                        {doc.metadatos_extraidos && (
                          <div className="mt-2 bg-blue-50 p-2 rounded border border-blue-100">
                            <p className="text-xs text-blue-700 font-bold">Metadatos Extraídos (IA):</p>
                            <pre className="text-xs text-blue-700 font-mono whitespace-pre-wrap">{JSON.stringify(JSON.parse(doc.metadatos_extraidos), null, 2)}</pre>
                          </div>
                        )}
                      </div>
                      {!doc.hash_firma && (
                        <button 
                          onClick={() => handleSignDocument(doc.id)}
                          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold hover:bg-blue-700 shadow-sm transition"
                        >
                          Firmar Digitalmente
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'trazabilidad' && (
              <div className="space-y-4">
                {trazabilidad.map(log => (
                  <div key={log.id} className="flex gap-4 p-3 border-l-4 border-blue-500 bg-gray-50 rounded-r-lg">
                    <div className="text-xs font-mono text-gray-400 whitespace-nowrap pt-1">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">{log.accion}</p>
                      <p className="text-sm text-gray-600">{log.descripcion}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'finanzas' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-gray-900">Facturas Asociadas</h3>
                  <button 
                    onClick={async () => {
                      const numero = prompt("Número de factura:");
                      const monto = prompt("Monto:");
                      const proveedor = prompt("Proveedor:");
                      if (numero && monto) {
                        try {
                          await api.post('/finanzas/facturas', {
                            numero,
                            monto: parseFloat(monto),
                            proveedor,
                            fecha_emision: new Date().toISOString(),
                            expediente_id: parseInt(id)
                          });
                          fetchData();
                        } catch (e) {
                          alert("Error registrando factura: " + e.message);
                        }
                      }
                    }}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm"
                  >
                    + Registrar Factura
                  </button>
                </div>
                
                {facturas.length === 0 ? <p className="text-gray-500 italic">No hay facturas registradas.</p> : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-500">
                      <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                          <th className="px-6 py-3">Número</th>
                          <th className="px-6 py-3">Proveedor</th>
                          <th className="px-6 py-3">Fecha</th>
                          <th className="px-6 py-3">Monto</th>
                          <th className="px-6 py-3">Estado</th>
                        </tr>
                      </thead>
                      <tbody>
                        {facturas.map((fac) => (
                          <tr key={fac.id} className="bg-white border-b hover:bg-gray-50">
                            <td className="px-6 py-4 font-medium text-gray-900">{fac.numero}</td>
                            <td className="px-6 py-4">{fac.proveedor}</td>
                            <td className="px-6 py-4">{new Date(fac.fecha_emision).toLocaleDateString()}</td>
                            <td className="px-6 py-4 font-bold text-gray-900">{fac.monto} €</td>
                            <td className="px-6 py-4">
                              <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                                fac.estado === 'PAGADA' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {fac.estado}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Detalles</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-500 block">Responsable</label>
                <p className="text-sm font-medium text-gray-900">ID Usuario: {expediente.responsable_id || 'Sin asignar'}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500 block">Fecha Creación</label>
                <p className="text-sm font-medium text-gray-900">{new Date(expediente.fecha_creacion).toLocaleDateString()}</p>
              </div>
              <div>
                <label className="text-xs text-gray-500 block">Última Actualización</label>
                <p className="text-sm font-medium text-gray-900">{new Date(expediente.fecha_actualizacion).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
