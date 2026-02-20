import { Layout } from "../components/Layout";

export function Dashboard() {
  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to Olympus Smart Gov</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900">Expedientes</h2>
          <p className="text-3xl font-bold text-blue-600 mt-2">-</p>
          <p className="text-gray-600 mt-2">Case files in progress</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900">Presupuesto</h2>
          <p className="text-3xl font-bold text-green-600 mt-2">$0.00</p>
          <p className="text-gray-600 mt-2">Budget execution</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900">Facturas</h2>
          <p className="text-3xl font-bold text-orange-600 mt-2">-</p>
          <p className="text-gray-600 mt-2">Pending invoices</p>
        </div>
      </div>
    </Layout>
  );
}
